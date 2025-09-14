using System;
using System.Net.Http;
using System.Threading.Tasks;
using Newtonsoft.Json;
using Microsoft.Maui.Controls;

namespace TestApp
{
    public partial class LoginPage : ContentPage
    {
        public static string CurrentUsername { get; private set; }

        public LoginPage()
        {
            InitializeComponent();
            #if ANDROID || IOS
                        NavigationPage.SetHasNavigationBar(this, true); // sau false dac? vrei s? ascunzi bara complet
                        NavigationPage.SetHasBackButton(this, false);
            #endif

            Shell.SetFlyoutBehavior(this, FlyoutBehavior.Disabled);

        }

        protected override void OnAppearing()
        {
            base.OnAppearing();
            if (SignUpPage.ShouldClearLoginFields)
            {
                UsernameEntry.Text = string.Empty;
                PasswordEntry.Text = string.Empty;
                SignUpPage.ShouldClearLoginFields = false;
            }
        }

        private async void OnLoginClicked(object sender, EventArgs e)
        {
            var username = UsernameEntry.Text;
            var password = PasswordEntry.Text;

            try
            {
                var response = await LoginAsync(username, password);

                if (response != null)
                {
                    CurrentUsername = username;
                    if (response.Role == "User")
                    {
                        await Navigation.PushAsync(new DetectPage());
                    }
                    else if (response.Role == "Partner")
                    {
                        await Navigation.PushAsync(new AdminPage());
                    }
                }
                else
                {
                    await DisplayAlert("Eroare", "Username or Password incorrect!", "OK");
                }
            }
            catch (Exception ex)
            {
                await DisplayAlert("Error", ex.Message, "OK");
            }
        }

        private async Task<UserResponse> LoginAsync(string username, string password)
        {
            try
            {
                using (var client = new HttpClient())
                using (var form = new MultipartFormDataContent())
                {
                    form.Add(new StringContent(username), "username");
                    form.Add(new StringContent(password), "password");
                    var response = await client.PostAsync("your_url", form);
                    if (response.IsSuccessStatusCode)
                    {
                        var json = await response.Content.ReadAsStringAsync();
                        return JsonConvert.DeserializeObject<UserResponse>(json);
                    }
                    else if (response.StatusCode == System.Net.HttpStatusCode.Unauthorized)
                    {
                        return null;
                    }
                    else
                    {
                        throw new Exception("Server error");
                    }

                }
            }
            catch (Exception ex)
            {
                string cleanMessage = ex.Message;
                int parenIndex = cleanMessage.IndexOf(" (");
                if (parenIndex > 0)
                {
                    cleanMessage = cleanMessage.Substring(0, parenIndex).Trim();
                }

                throw new Exception(cleanMessage);
            }
        }

        private async void OnSignUpButtonClicked(object sender, EventArgs e)
        {

            await Navigation.PushAsync(new SignUpPage());
        }
        protected override bool OnBackButtonPressed()
        {
            Device.BeginInvokeOnMainThread(async () =>
            {
                bool exit = await DisplayAlert("Exit", "You want to exit?", "Yes", "No");
                if (exit)
                {
                    #if IOS
                                        // iOS nu permite închiderea aplica?iei
                                        Console.WriteLine("Exit not supported on iOS");
                    #else
                                System.Diagnostics.Process.GetCurrentProcess().Kill();
                    #endif
                }
            });

            return true;
        }



    }

    public class UserResponse
    {
        public string Role { get; set; }
        public string Username { get; set; }
        public string Message { get; set; }
    }
}