// DetectPage.xaml.cs
using Newtonsoft.Json;


namespace TestApp
{
    public partial class DetectPage : ContentPage
    {
        private List<string> selectedImagePaths = new List<string>();

        private const string ApiUrl = "your_url";


        public DetectPage()
        {
            InitializeComponent();

             Shell.SetFlyoutBehavior(this, FlyoutBehavior.Disabled);

            includeCarDataSwitch.Toggled += (s, e) =>
            {
                manufactureEntry.IsVisible = e.Value;
                carModelEntry.IsVisible = e.Value;
                yearEntry.IsVisible = e.Value;
            };

            pickImageButton.Clicked += PickImages;
            detectButton.Clicked += StartDetection;
            resetButton.Clicked += ResetDetection;

           

        }

        private async void PickImages(object sender, EventArgs e)
        {
            try
            {
                var results = await FilePicker.PickMultipleAsync(new PickOptions
                {
                    PickerTitle = "Select one or more images",
                    FileTypes = FilePickerFileType.Images
                });

                if (results != null && results.Any())
                {
                    selectedImagePaths.Clear();
                    imagesContainer.Children.Clear();

                    foreach (var result in results)
                    {
                        selectedImagePaths.Add(result.FullPath);
                        var image = new Image
                        {
                            HeightRequest = 300,
                            WidthRequest = 300,
                            Aspect = Aspect.AspectFit,
                            Source = ImageSource.FromFile(result.FullPath)
                        };
                        var label = new Label
                        {
                            Text = $"Image: {Path.GetFileName(result.FullPath)}",
                            FontSize = 12,
                            TextColor = Colors.LightGray
                        };
                        imagesContainer.Children.Add(label);
                        imagesContainer.Children.Add(image);
                    }

                    detectButton.IsEnabled = true;
                    resultLabel.Text = $"{selectedImagePaths.Count} images selected.";
                    resetButton.IsVisible = false;
                    servicesHeader.IsVisible = false;
                }
              
            
            }
            catch (Exception ex)
            {
                await ShowCleanError($"Selection error: {ex.Message}");
                resultLabel.Text = string.Empty;
            }
        }
        private async void StartDetection(object sender, EventArgs e)
        {
            if (selectedImagePaths.Any())
            {
                if (includeCarDataSwitch.IsToggled)
                {
                    if (string.IsNullOrEmpty(manufactureEntry.Text) || string.IsNullOrEmpty(carModelEntry.Text) || string.IsNullOrEmpty(yearEntry.Text))
                    {
                        await ShowCleanError("All fields are required!");
                        return;
                    }
                    if (!int.TryParse(yearEntry.Text, out int year) || year < 1900 || year > DateTime.Now.Year)
                    {
                        await ShowCleanError("Year must be a valid number between 1900 and the current year!");
                        return;
                    }
                }

                resultLabel.Text = "Is being processed...";
                await MainThread.InvokeOnMainThreadAsync(() => 
                {
                    pickImageButton.IsVisible = false;
                    detectButton.IsVisible = false; 
                    resetButton.IsVisible = true; 
                    pickImageButton.IsEnabled = false;
                    includeCarDataSwitch.IsEnabled = false;
                    manufactureEntry.IsEnabled = false;
                    carModelEntry.IsEnabled = false;
                    yearEntry.IsEnabled = false;
                });
                await SendImageToServer(selectedImagePaths); 
            }
            else
            {
                resultLabel.Text = "You have not selected any images!";
            }
        }

        private async void ResetDetection(object sender, EventArgs e)
        {
            bool confirmReset = await DisplayAlert("Confirm", "Do you want to restart?", "Yes", "No");
            if (confirmReset)
            {

                imagesContainer.Children.Clear();
                selectedImagePaths.Clear();
                detectButton.IsEnabled = false;
                detectButton.IsVisible = true;
                resetButton.IsVisible = false;
                resultLabel.Text = null;
                manufactureEntry.Text = string.Empty;
                carModelEntry.Text = string.Empty;
                yearEntry.Text = string.Empty;
                includeCarDataSwitch.IsToggled = false;
                servicesHeader.IsVisible = false;
                pickImageButton.IsEnabled = true;
                includeCarDataSwitch.IsEnabled = true;
                manufactureEntry.IsEnabled = true;
                carModelEntry.IsEnabled = true;
                yearEntry.IsEnabled = true;
                pickImageButton.IsVisible = true;

            }
        }

        private async Task SendImageToServer(List<string> imagePaths)
        {

            try
            {
                using (var client = new HttpClient())
                using (var form = new MultipartFormDataContent())
                {
                    foreach (var imagePath in imagePaths)
                    {
                        using var stream = File.OpenRead(imagePath);
                        using var ms = new MemoryStream();
                        await stream.CopyToAsync(ms);
                        byte[] imageBytes = ms.ToArray();

                        form.Add(new ByteArrayContent(imageBytes), "images", Path.GetFileName(imagePath));
                    }

                    Console.WriteLine($"Sending: username={LoginPage.CurrentUsername}, manufacturer={manufactureEntry.Text}, car_model={carModelEntry.Text}, year={yearEntry.Text}");
                    form.Add(new StringContent(LoginPage.CurrentUsername), "username");

                    if (includeCarDataSwitch.IsToggled)
                    {
                        form.Add(new StringContent(manufactureEntry.Text?.Trim() ?? ""), "manufacturer");
                        form.Add(new StringContent(carModelEntry.Text?.Trim() ?? ""), "car_model");
                        form.Add(new StringContent(yearEntry.Text?.Trim() ?? ""), "year");
                    }

                    HttpResponseMessage response = await client.PostAsync(ApiUrl, form);
                    string result = await response.Content.ReadAsStringAsync();

                    if (!response.IsSuccessStatusCode)
                    {
                        await MainThread.InvokeOnMainThreadAsync(async () =>
                        {
                            await ShowCleanError($"Server error: {result}");
                            resultLabel.Text = string.Empty;
                        });
                        return;
                    }

                    Dictionary<string, object> responseData;
                    try
                    {
                        responseData = JsonConvert.DeserializeObject<Dictionary<string, object>>(result);
                    }
                    catch (JsonException ex)
                    {
                        await MainThread.InvokeOnMainThreadAsync(async () =>
                        {
                            await ShowCleanError($"Invalid response format: {ex.Message}");
                            resultLabel.Text = string.Empty;
                        });
                        return;
                    }

                    if (responseData.ContainsKey("error"))
                    {
                        await MainThread.InvokeOnMainThreadAsync(async () =>
                        {
                            await ShowCleanError(responseData["error"].ToString());
                            resultLabel.Text = string.Empty;
                        });
                        return;
                    }

                    string message = responseData["message"]?.ToString() ?? "Processing completed";
                    var detectedParts = JsonConvert.DeserializeObject<Dictionary<string, Dictionary<string, object>>>(responseData["detected_parts"].ToString());
                    var annotatedImages = JsonConvert.DeserializeObject<Dictionary<string, string>>(responseData["annotated_images"].ToString());
                    var serviceInfo = responseData.ContainsKey("service_info")
                        ? JsonConvert.DeserializeObject<Dictionary<string, List<Dictionary<string, object>>>>(responseData["service_info"].ToString())
                        : new Dictionary<string, List<Dictionary<string, object>>>();

                    Console.WriteLine($"Received service_info: {JsonConvert.SerializeObject(serviceInfo)}");

                    await MainThread.InvokeOnMainThreadAsync(async () =>
                    {
                        await ShowSuccessMessage(message);
                        resultLabel.Text = string.Empty;

                        imagesContainer.Children.Clear();

                        foreach (var kvp in annotatedImages)
                        {
                            string key = kvp.Key;
                            string base64Img = kvp.Value.Replace("data:image/jpeg;base64,", "");
                            byte[] annotatedBytes = Convert.FromBase64String(base64Img);

                            var image = new Image
                            {
                                HeightRequest = 300,
                                WidthRequest = 300,
                                Aspect = Aspect.AspectFit,
                                Source = ImageSource.FromStream(() => new MemoryStream(annotatedBytes))
                            };

                            var label = new Label
                            {
                                Text = key.Contains("original") ? $"Original image {key.Split('_')[1]}" : $"Final annotation for {key.Split('_')[0]}",
                                FontSize = 12,
                                TextColor = Colors.LightGray
                            };

                            imagesContainer.Children.Add(label);
                            imagesContainer.Children.Add(image);
                        }

                        Console.WriteLine($"ServiceInfo count: {serviceInfo.Count}");
                        if (serviceInfo.Any())
                        {
                            Console.WriteLine($"First serviceInfo value count: {serviceInfo.First().Value.Count}");
                            foreach (var service in serviceInfo.First().Value)
                            {
                                Console.WriteLine($"Service: {service["ServiceName"]}, Has Price: {service.ContainsKey("Price")}, Has ComponentName: {service.ContainsKey("ComponentName")}");
                            }
                        }

                        servicesHeader.IsVisible = true;

                        if (serviceInfo.Any() && serviceInfo.First().Value.Any())
                        {
                            bool hasComponentDetails = serviceInfo.Any(part => part.Value.Any(s =>
                                s.ContainsKey("Price") && Convert.ToDouble(s["Price"]) > 0 &&
                                s.ContainsKey("LaborCost") && Convert.ToDouble(s["LaborCost"]) > 0 &&
                                !string.IsNullOrEmpty(s["ComponentName"]?.ToString()) &&
                                !string.IsNullOrEmpty(s["ComponentCode"]?.ToString())));

                            if (hasComponentDetails)
                            {
                                var allServices = new Dictionary<string, Dictionary<string, object>>();
                                foreach (var partList in serviceInfo.Values)
                                {
                                    foreach (var info in partList)
                                    {
                                        string serviceName = info["ServiceName"].ToString();
                                        if (!allServices.ContainsKey(serviceName) ||
                                            string.IsNullOrEmpty(allServices[serviceName]["ComponentName"]?.ToString()))
                                        {
                                            allServices[serviceName] = info;
                                        }
                                    }
                                }

                                var groupedByService = new Dictionary<string, List<(string Part, Dictionary<string, object> Info)>>();
                                foreach (var partEntry in serviceInfo)
                                {
                                    var part = partEntry.Key;
                                    var infoList = partEntry.Value;
                                    if (infoList != null && infoList.Any())
                                    {
                                        foreach (var info in infoList)
                                        {
                                            string serviceName = info["ServiceName"].ToString();
                                            if (!groupedByService.ContainsKey(serviceName))
                                            {
                                                groupedByService[serviceName] = new List<(string, Dictionary<string, object>)>();
                                            }
                                            if (!string.IsNullOrEmpty(info["ComponentName"]?.ToString()))
                                            {
                                                groupedByService[serviceName].Add((part, info));
                                            }
                                        }
                                    }
                                }

                                foreach (var serviceName in allServices.Keys)
                                {
                                    if (!groupedByService.ContainsKey(serviceName))
                                    {
                                        groupedByService[serviceName] = new List<(string, Dictionary<string, object>)>();
                                    }
                                }

                                foreach (var serviceGroup in groupedByService.OrderBy(s => s.Key))
                                {
                                    string serviceName = serviceGroup.Key;
                                    var components = serviceGroup.Value;
                                    var serviceInfo = allServices[serviceName];

                                    var serviceFrame = new Frame
                                    {
                                        BackgroundColor = Color.FromArgb("#2A2A2A"),
                                        CornerRadius = 15,
                                        Padding = new Thickness(15),
                                        Margin = new Thickness(0, 10),
                                        HasShadow = false
                                    };

                                    var serviceStack = new VerticalStackLayout
                                    {
                                        Spacing = 5
                                    };

                                    var serviceLabel = new Label
                                    {
                                        Text = serviceName,
                                        FontSize = 16,
                                        FontAttributes = FontAttributes.Bold,
                                        TextColor = Colors.White
                                    };

                                    var detailsLabel = new Label
                                    {
                                        Text = $"Location: {serviceInfo["ServiceLocation"]}, Email: {serviceInfo["Email"]}, Phone: {serviceInfo["Number"]}",
                                        FontSize = 14,
                                        TextColor = Colors.LightGray
                                    };

                                    serviceStack.Children.Add(serviceLabel);
                                    serviceStack.Children.Add(detailsLabel);

                                    if (components.Any())
                                    {
                                        double totalPrice = 0;
                                        double totalLaborCost = 0;

                                        foreach (var (part, info) in components)
                                        {
                                            double price = Convert.ToDouble(info["Price"]);
                                            double laborCost = Convert.ToDouble(info["LaborCost"]);
                                            double componentTotal = price + laborCost;
                                            totalPrice += price;
                                            totalLaborCost += laborCost;

                                            var componentLabel = new Label
                                            {
                                                Text = $"{info["ComponentName"]}, Code: {info["ComponentCode"]}, Price: {price} RON, Labor Cost: {laborCost} RON, Total: {componentTotal} RON",
                                                FontSize = 14,
                                                TextColor = Colors.LightGray
                                            };
                                            serviceStack.Children.Add(componentLabel);
                                        }

                                        double grandTotal = totalPrice + totalLaborCost;
                                        var totalsLabel = new Label
                                        {
                                            Text = $"Total Price: {totalPrice} RON, Total Labor Cost: {totalLaborCost} RON, Grand Total: {grandTotal} RON",
                                            FontSize = 14,
                                            FontAttributes = FontAttributes.Bold,
                                            TextColor = Colors.Green
                                        };
                                        serviceStack.Children.Add(totalsLabel);
                                    }
                                    else
                                    {
                                        var noComponentsLabel = new Label
                                        {
                                            Text = "No components available for this service.",
                                            FontSize = 14,
                                            TextColor = Colors.LightGray
                                        };
                                        serviceStack.Children.Add(noComponentsLabel);
                                    }

                                    serviceFrame.Content = serviceStack;
                                    imagesContainer.Children.Add(serviceFrame);
                                }

                                if (!groupedByService.Any())
                                {
                                    var noInfoFrame = new Frame
                                    {
                                        BackgroundColor = Color.FromArgb("#2A2A2A"),
                                        CornerRadius = 15,
                                        Padding = new Thickness(15),
                                        Margin = new Thickness(0, 10),
                                        HasShadow = false
                                    };

                                    var noInfoLabel = new Label
                                    {
                                        Text = "No service information available.",
                                        FontSize = 14,
                                        TextColor = Colors.LightGray
                                    };

                                    noInfoFrame.Content = noInfoLabel;
                                    imagesContainer.Children.Add(noInfoFrame);
                                }
                            }
                            else
                            {
                                var services = serviceInfo.First().Value
                                    .GroupBy(s => new { Name = s["ServiceName"].ToString(), Location = s["ServiceLocation"].ToString(), Email = s["Email"].ToString(), Number = s["Number"].ToString() })
                                    .Select(g => new
                                    {
                                        g.Key.Name,
                                        g.Key.Location,
                                        g.Key.Email,
                                        g.Key.Number
                                    });

                                foreach (var service in services)
                                {
                                    var serviceFrame = new Frame
                                    {
                                        BackgroundColor = Color.FromArgb("#2A2A2A"),
                                        CornerRadius = 15,
                                        Padding = new Thickness(15),
                                        Margin = new Thickness(0, 5),
                                        HasShadow = false
                                    };

                                    var serviceStack = new VerticalStackLayout
                                    {
                                        Spacing = 5
                                    };

                                    var nameLabel = new Label
                                    {
                                        Text = service.Name,
                                        FontSize = 16,
                                        FontAttributes = FontAttributes.Bold,
                                        TextColor = Colors.White
                                    };

                                    var detailsLabel = new Label
                                    {
                                        Text = $"Location: {service.Location}",
                                        FontSize = 14,
                                        TextColor = Colors.LightGray
                                    };

                                    var contactLabel = new Label
                                    {
                                        Text = $"Email: {service.Email}, Phone: {service.Number}",
                                        FontSize = 14,
                                        TextColor = Colors.LightGray
                                    };

                                    serviceStack.Children.Add(nameLabel);
                                    serviceStack.Children.Add(detailsLabel);
                                    serviceStack.Children.Add(contactLabel);
                                    serviceFrame.Content = serviceStack;
                                    imagesContainer.Children.Add(serviceFrame);
                                }

                                if (!services.Any())
                                {
                                    var noInfoFrame = new Frame
                                    {
                                        BackgroundColor = Color.FromArgb("#2A2A2A"),
                                        CornerRadius = 15,
                                        Padding = new Thickness(15),
                                        Margin = new Thickness(0, 5),
                                        HasShadow = false
                                    };

                                    var noInfoLabel = new Label
                                    {
                                        Text = "No services available.",
                                        FontSize = 14,
                                        TextColor = Colors.LightGray
                                    };

                                    noInfoFrame.Content = noInfoLabel;
                                    imagesContainer.Children.Add(noInfoFrame);
                                }
                            }
                        }
                        else
                        {
                            var noInfoFrame = new Frame
                            {
                                BackgroundColor = Color.FromArgb("#2A2A2A"),
                                CornerRadius = 15,
                                Padding = new Thickness(15),
                                Margin = new Thickness(0, 5),
                                HasShadow = false
                            };

                            var noInfoLabel = new Label
                            {
                                Text = "No services available.",
                                FontSize = 14,
                                TextColor = Colors.LightGray
                            };

                            noInfoFrame.Content = noInfoLabel;
                            imagesContainer.Children.Add(noInfoFrame);
                        }
                    });
                }
            }
            catch (Exception ex)
            {
                await MainThread.InvokeOnMainThreadAsync(async () =>
                {
                    await ShowCleanError($"Processing error: {ex.Message}");
                    resultLabel.Text = string.Empty;
                });
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

        private async Task ShowSuccessMessage(string message)
        {
            await DisplayAlert("Succes", message, "OK");
        }
    }
}