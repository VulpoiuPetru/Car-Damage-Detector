using System.Diagnostics;
using System.Net.Http;
using System.Net.Http.Headers;
using System.IO;
using System.Threading.Tasks;
using Newtonsoft.Json;
using Microsoft.Maui.Controls;
using System.Text;


namespace TestApp
{
    public partial class MainPage : ContentPage
    {
        public MainPage()
        {
            InitializeComponent();

            Shell.SetFlyoutBehavior(this, FlyoutBehavior.Disabled);

            #if ANDROID || IOS
                        NavigationPage.SetHasNavigationBar(this, true);
                        NavigationPage.SetHasBackButton(this, false);
            #endif
            NavigationPage.SetTitleView(this, new Label());


            this.SizeChanged += OnPageSizeChanged;

            StartSequenceAsync();

          
        }


        private async Task StartSequenceAsync()
        {
            await Task.Delay(2300);

            await TitleLayout.FadeTo(1, 2000);

            await Navigation.PushAsync(new LoginPage());
        }

        private void OnPageSizeChanged(object sender, EventArgs e)
        {
            double screenWidth = this.Width;
            double screenHeight = this.Height;

            if (screenWidth <= 0 || screenHeight <= 0)
                return;

            double aspectRatio = 16.0 / 9.0;

            double targetHeight = screenHeight;
            double targetWidth = targetHeight * aspectRatio * 0.85;

            if (targetWidth < screenWidth)
            {
                targetWidth = screenWidth;
                targetHeight = targetWidth / aspectRatio;
            }

            LottieAnimation.WidthRequest = targetWidth;
            LottieAnimation.HeightRequest = targetHeight;

        }

    }


}