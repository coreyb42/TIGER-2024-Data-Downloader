# TIGER 2024 Data Downloader

## Overview
This script recursively downloads TIGER 2024 shapefiles from the U.S. Census Bureau's website and saves them to a specified local directory. It includes features such as:

- **Automatic Resumption**: Skips existing files to avoid redundant downloads.
- **Retry Logic**: Retries failed downloads up to 3 times.
- **Logging**: Provides detailed logs on progress and errors.
- **Progress Bars**: Uses `tqdm` to show download progress.

## Prerequisites
This script requires Python 3 and the following dependencies:

- `requests`
- `beautifulsoup4`
- `tqdm`

You can install them with:

```sh
pip install requests beautifulsoup4 tqdm
```

## Setup
1. **Clone the repository**
   ```sh
   git clone https://github.com/coreyb42/TIGER-2024-Data-Downloader.git
   cd tiger2024-downloader
   ```

2. **Modify the destination path**
   - Open `download_tiger2024.py` and change `DEST_DIR` to your desired download directory.
   ```python
   DEST_DIR = "<YOUR_DESTINATION_PATH>"  # Replace with your actual path
   ```

3. **Run the script**
   ```sh
   python download_tiger2024.py
   ```

## How It Works
1. The script starts at the TIGER 2024 directory and fetches all subfolders and files.
2. It checks if a file already exists before downloading.
3. If a request fails, it retries up to 3 times before skipping.
4. It logs progress and errors for easy debugging.

## Contributing
If you find issues or have improvements, feel free to submit a pull request!

## License
This project is licensed under the MIT License. See `LICENSE` for details.
