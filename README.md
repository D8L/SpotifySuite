# SpotifySuite

A lightweight, terminal-based program to sort and pull your Spotify information by utilizing their API.

## Getting Started

Follow these steps to set up the project on your local machine:

## Creating the Spotify Application
For **SpotifySuite** to function you need to create a Spotify application through the [developer dashboard.](https://developer.spotify.com/dashboard/applications)
1. Click on **Create app**.
2. Fill out the information.
3. Paste http://127.0.0.1:9492 for **Redirect URI** — any port works.
4. Navigate to the **Settings** of the app.
5. Save the **Client ID** and **Client Secret** for the next instructions.

## Running Spotify Suite

1. Clone the repository:

```
git clone https://github.com/D8L/SpotifySuite.git
```

2. Navigate to the project directory:

```
cd SpotifySuite
```

3. Install dependencies:

```
pip install -r requirements.txt
```

4. Edit the .env file in the main directory:

```
export SPOTIPY_CLIENT_ID=<CLIENT_ID_FROM_EARLIER>
export SPOTIPY_CLIENT_SECRET=<SECRET_ID_FROM_EARLIER>
export SPOTIPY_REDIRECT_URI='http://127.0.0.1:9492'
```

5. Start the app:
```
python3 main.py
```

## Built With

* Python
* Spotify API
* Spotipy

## Authors

* D8L
* vin33th1

## License

This project is licensed under the MIT License - see the [LICENSE.md](https://github.com/D8L/PaintingTracker/blob/main/LICENSE.md) file for details
