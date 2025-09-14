// SignUpPage.xaml.cs
using Newtonsoft.Json;
using System.Text;


namespace TestApp
{
    public partial class SignUpPage : ContentPage
    {

        private string sentCode = "";
        public static bool ShouldClearLoginFields { get; set; }

        public SignUpPage()
        {
            InitializeComponent();

            Shell.SetFlyoutBehavior(this, FlyoutBehavior.Disabled);


            RolePicker.ItemsSource = new List<string> { "User", "Partner" };
            RolePicker.SelectedIndex = 0;

            ShouldClearLoginFields = false;

        }
        private void OnRoleChanged(object sender, EventArgs e)
        {
            bool isPartner = RolePicker.SelectedItem?.ToString() == "Partner";

            PartnerEmailEntry.IsVisible = isPartner;
            GenerateCodeButton.IsVisible = isPartner;
            CodeEntry.IsVisible = isPartner;
            ConfirmCodeButton.IsVisible = isPartner;

            CompanyNameEntry.IsVisible = false;
            CompanyNumberEntry.IsVisible = false;
            CompanyLocationEntry.IsVisible = false;
        }
        private async void OnGenerateCodeClicked(object sender, EventArgs e)
        {
            var email = PartnerEmailEntry.Text;
            if (string.IsNullOrEmpty(email))
            {
                await DisplayAlert("Error", "Email is required.", "OK");
                return;
            }

            try
            {
                using var client = new HttpClient();
                var form = new MultipartFormDataContent();
                form.Add(new StringContent(email), "email");
                var response = await client.PostAsync("your_url/send-code/", form);


                if (response.IsSuccessStatusCode)
                {
                    var json = await response.Content.ReadAsStringAsync();
                    var data = Newtonsoft.Json.JsonConvert.DeserializeObject<Dictionary<string, string>>(json);

                    if (data.ContainsKey("code"))
                    {
                        sentCode = data["code"];
                        await DisplayAlert("Sent", $"The code was sent to {email}.", "OK");
                    }
                    else
                    {
                        await DisplayAlert("Error", "No code received from server!", "OK");
                    }
                }
                else
                {
                    var message = await response.Content.ReadAsStringAsync();
                    await DisplayAlert("Error", message, "OK");
                }
            }
            catch (Exception ex)
            {
                await ShowCleanError(ex.Message);
            }
        }

        private async void OnConfirmCodeClicked(object sender, EventArgs e)
        {
            if (CodeEntry.Text == sentCode)
            {
                await DisplayAlert("Confirmed", "The code is correct!", "OK");

                CompanyNameEntry.IsVisible = true;
                CompanyNumberEntry.IsVisible = true;
                CompanyLocationEntry.IsVisible = true;
            }
            else
            {
                await DisplayAlert("Error", "The code is incorrect!", "OK");
            }
        }
        private async void OnSignUpClicked(object sender, EventArgs e)
        {
            var username = UsernameEntry.Text;
            var password = PasswordEntry.Text;
            var role = RolePicker.SelectedItem?.ToString();
            var companyNumber = CompanyNumberEntry.Text;
            var companyEmail = PartnerEmailEntry.Text;
            var companyName = CompanyNameEntry.Text;
            var companyLocation = CompanyLocationEntry.Text;


            if (role == "User")
            {
                if (string.IsNullOrEmpty(username) || string.IsNullOrEmpty(password) || string.IsNullOrEmpty(role))
                {
                    await DisplayAlert("Eroare", "All fields are required!", "OK");
                    return;
                }


                var success = await SignUpAsyncUser(username, password, role);
                if (success)
                {
                    ShouldClearLoginFields = true;

                    await DisplayAlert("Success", "The account was created successfully!", "OK");
                    await Navigation.PopAsync();
                    
                }
            }
            else
            if(role == "Partner")
            {
                if (string.IsNullOrEmpty(username) || string.IsNullOrEmpty(password) || string.IsNullOrEmpty(role) || string.IsNullOrEmpty(companyNumber) ||
                 string.IsNullOrEmpty(companyEmail) || string.IsNullOrEmpty(companyName) || string.IsNullOrEmpty(companyLocation))
                {
                    await DisplayAlert("Eroare", "All fields are required!", "OK");
                    return;
                }
                var success = await SignUpAsyncPartner(username, password, role, companyName, companyNumber, companyEmail,companyLocation);
                if (success)
                {
                    ShouldClearLoginFields = true;
                    await DisplayAlert("Success", "The account was created successfully!", "OK");
                    await Navigation.PopAsync();
                }
            }
            

        }

        private async Task<bool> SignUpAsyncPartner(string username, string password, string role, string companyName, string companyNumber, string companyEmail, string companyLocation)
        {
            try
            {
                using (var client = new HttpClient())
                using (var form = new MultipartFormDataContent())
                {
                    form.Add(new StringContent(username), "username");
                    form.Add(new StringContent(password), "password");
                    form.Add(new StringContent(role), "role");
                    form.Add(new StringContent(companyName), "company_name");
                    form.Add(new StringContent(companyNumber), "company_number");
                    form.Add(new StringContent(companyEmail), "company_email");
                    form.Add(new StringContent(companyLocation), "company_location");

                     var response = await client.PostAsync("your_url/signupPartner/", form);
                    if (response.IsSuccessStatusCode)
                    {
                        return true;
                    }
                    else
                    {
                        var message = await response.Content.ReadAsStringAsync();
                        await DisplayAlert("Error", message, "OK");
                        return false;
                    }
                }
            }
            catch (Exception ex)
            {
                await ShowCleanError(ex.Message);

                return false;
            }
        }

        private async Task<bool> SignUpAsyncUser(string username, string password, string role)
        {
            try
            {
                using (var client = new HttpClient())
                using (var form = new MultipartFormDataContent())
                {
                    form.Add(new StringContent(username), "username");
                    form.Add(new StringContent(password), "password");
                    form.Add(new StringContent(role), "role");

                    var response = await client.PostAsync("your_url/signupUser/", form);

                    if (response.IsSuccessStatusCode)
                    {
                        return true;
                    }
                    else
                    {
                        var message = await response.Content.ReadAsStringAsync();
                        await DisplayAlert("Error", message, "OK");

                        return false;
                    }
                }
            }
            catch (Exception ex)
            {
                await ShowCleanError(ex.Message);

                return false;
            }
        }
        private async Task ShowCleanError(string rawMessage)
        {
            string cleanMessage = rawMessage;

            int parenIndex = cleanMessage.IndexOf(" (");
            if (parenIndex > 0)
            {
                cleanMessage = cleanMessage.Substring(0, parenIndex).Trim();
            }

            await DisplayAlert("Error", cleanMessage, "OK");
        }

    }
}
