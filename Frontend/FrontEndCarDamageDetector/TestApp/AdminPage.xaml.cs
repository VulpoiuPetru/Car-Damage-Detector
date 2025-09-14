using Microsoft.Maui.Controls;
using System;
using System.Net.Http;
using System.Threading.Tasks;
using System.IO;
using System.Collections.Generic;
using System.Text.Json;

namespace TestApp
{
    public partial class AdminPage : ContentPage
    {
       
        private List<(int FileId, string Filename)> csvFiles;

        private const string BaseUrl = "your_url"

        private static readonly FilePickerFileType CsvFileType = new FilePickerFileType(
            new Dictionary<DevicePlatform, IEnumerable<string>>
            {
                { DevicePlatform.Android, new[] { "text/csv" } },
                { DevicePlatform.iOS, new[] { "public.csv" } },
                { DevicePlatform.WinUI, new[] { ".csv" } }
            });

        public AdminPage()
        {
            InitializeComponent();

            Shell.SetFlyoutBehavior(this, FlyoutBehavior.Disabled);


            uploadCsvButton.Clicked += OnUploadCsvClicked;
            deleteCsvButton.Clicked += OnDeleteCsvClicked;
            csvPicker.SelectedIndexChanged += CsvPicker_SelectedIndexChanged;

            LoadCsvList();
        }
        private async void LoadCsvList()
        {
            try
            {
                using (var client = new HttpClient())
                {
                    var response = await client.GetAsync($"{BaseUrl}/list_csvs/?username={LoginPage.CurrentUsername}");
                    if (response.IsSuccessStatusCode)
                    {
                        var json = await response.Content.ReadAsStringAsync();
                        var data = JsonSerializer.Deserialize<Dictionary<string, List<Dictionary<string, JsonElement>>>>(json);
                        csvFiles = new List<(int, string)>();

                        foreach (var file in data["files"])
                        {
                            int fileId = file["file_id"].GetInt32(); 
                            string filename = file["filename"].GetString();
                            csvFiles.Add((fileId, filename));
                        }

                        csvPicker.ItemsSource = csvFiles.ConvertAll(f => f.Filename);
                    }
                    else
                    {
                        await ShowCleanError("Error loading CSV list.");

                    }
                }
            }
            catch (Exception ex)
            {
                await ShowCleanError(ex.Message);
            }
        }

        private async void OnUploadCsvClicked(object sender, EventArgs e)
        {
            try
            {
                var result = await FilePicker.PickAsync(new PickOptions
                {
                    PickerTitle = "Select a CSV file",
                    FileTypes = CsvFileType
                });

                if (result == null)
                {
                    await ShowCleanError("No file selected.");

                    return;
                }

                var fileBytes = File.ReadAllBytes(result.FullPath);
                using (var client = new HttpClient())
                using (var form = new MultipartFormDataContent())
                {
                    form.Add(new ByteArrayContent(fileBytes), "file", result.FileName);
                    form.Add(new StringContent(LoginPage.CurrentUsername), "username");

                    var response = await client.PostAsync($"{BaseUrl}/upload_csv/", form);

                    if (response.IsSuccessStatusCode)
                    {
                        var responseContent = await response.Content.ReadAsStringAsync();
                        await ShowSuccessMessage(responseContent);
                        LoadCsvList();
                    }
                    else
                    {
                        var errorContent = await response.Content.ReadAsStringAsync();
                        await ShowCleanError(errorContent);
                    }
                }
            }
            catch (Exception ex)
            {
                await ShowCleanError($"Error while upload: {ex.Message}");

            }
        }


        private async void OnDeleteCsvClicked(object sender, EventArgs e)
        {
            try
            {
                if (csvPicker.SelectedIndex == -1)
                {
                    await ShowCleanError("Select a CSV file to delete.");
                    return;
                }

                var selectedFile = csvFiles[csvPicker.SelectedIndex];
                resultLabel.Text = $"Selected FileId: {selectedFile.FileId}";

                if (selectedFile.FileId <= 0)
                {
                    await ShowCleanError("Invalid field. Please try again.");
                    return;
                }

                using (var client = new HttpClient())
                using (var form = new MultipartFormDataContent())
                {
                    form.Add(new StringContent(selectedFile.FileId.ToString()), "file_id");
                    form.Add(new StringContent(LoginPage.CurrentUsername), "username");

                    var response = await client.PostAsync($"{BaseUrl}/delete_csv/", form);

                    if (response.IsSuccessStatusCode)
                    {
                        var responseContent = await response.Content.ReadAsStringAsync();
                        await ShowSuccessMessage(responseContent);
                        csvPicker.SelectedIndex = -1;
                        await LoadCsvListAsync(); 
                    }
                    else
                    {
                        var errorContent = await response.Content.ReadAsStringAsync();
                        await ShowCleanError(errorContent);

                    }
                }
            }

            catch (Exception ex)
            {
                await ShowCleanError($"Error while deleting: {ex.Message}");
            }
        }

        private async Task LoadCsvListAsync()
        {
            try
            {
                using (var client = new HttpClient())
                {
                    var response = await client.GetAsync($"{BaseUrl}/list_csvs/?username={LoginPage.CurrentUsername}");
                    if (response.IsSuccessStatusCode)
                    {
                        var json = await response.Content.ReadAsStringAsync();
                        var data = JsonSerializer.Deserialize<Dictionary<string, List<Dictionary<string, JsonElement>>>>(json);
                        csvFiles = new List<(int, string)>();

                        foreach (var file in data["files"])
                        {
                            int fileId = file["file_id"].GetInt32();
                            string filename = file["filename"].GetString();
                            csvFiles.Add((fileId, filename));
                        }

                        await Device.InvokeOnMainThreadAsync(() =>
                        {
                            csvPicker.ItemsSource = null; 
                            csvPicker.ItemsSource = csvFiles.ConvertAll(f => f.Filename);
                        });
                    }
                    else
                    {
                        await ShowCleanError("Error loading CSV list.");

                    }
                }
            }
            catch (Exception ex)
            {
                await ShowCleanError($"Error: {ex.Message}");
            }
        }

        public class CsvRow
        {
            public string Manufacturer { get; set; }
            public string CarModel { get; set; }
            public int Year { get; set; }
            public string ComponentCode { get; set; }
            public string Component { get; set; }
            public decimal Price { get; set; }
            public decimal LaborCost { get; set; }
        }


        private async void CsvPicker_SelectedIndexChanged(object sender, EventArgs e)
        {
            if (csvPicker.SelectedIndex == -1)
            {
                csvTableContainer.IsVisible = false;
                return;
            }

            var selectedFile = csvFiles[csvPicker.SelectedIndex];
            csvTableHeader.IsVisible = false; 
            csvTableContainer.IsVisible = false;

            try
            {
                using var client = new HttpClient();
                var response = await client.GetAsync($"{BaseUrl}/get_csv_data/?file_id={selectedFile.FileId}&username={LoginPage.CurrentUsername}");

                if (response.IsSuccessStatusCode)
                {
                    var content = await response.Content.ReadAsStringAsync();
                    var json = JsonSerializer.Deserialize<JsonElement>(content);

                    var rows = new List<CsvRow>();
                    foreach (var row in json.GetProperty("rows").EnumerateArray())
                    {
                        var csvRow = new CsvRow
                        {
                            Manufacturer = row[0].GetString(),
                            CarModel = row[1].GetString(),
                            Year = row[2].GetInt32(),
                            ComponentCode = row[3].GetString(),
                            Component = row[4].GetString(),
                            Price = row[5].GetDecimal(),
                            LaborCost = row[6].GetDecimal()
                        };
                        rows.Add(csvRow);
                    }

                    csvTableView.ItemsSource = rows;
                    csvTableHeader.IsVisible = true;
                    csvTableContainer.IsVisible = true; 
                }
                else
                {
                    var errorMsg = await response.Content.ReadAsStringAsync();
                    await ShowCleanError($"Error loading data: {errorMsg}");
                    csvTableView.ItemsSource = null; 
                }
            }
            catch (Exception ex)
            {
                await ShowCleanError($"Exception: {ex.Message}");
                csvTableView.ItemsSource = null;
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