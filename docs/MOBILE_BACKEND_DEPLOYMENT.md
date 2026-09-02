# BusCrowd Mobile + Backend Deployment

This project has one Flutter app with a Passenger role and a Conductor role. The conductor issues real tickets to the FastAPI backend. The backend updates deterministic live occupancy and, when Firebase Admin is configured, publishes the same live state to Firestore at `live_buses/{bus_id}` for instant passenger updates.

## 1. Install Local Tooling

```powershell
winget install Google.Chrome
winget install Git.Git
winget install OpenJS.NodeJS.LTS
winget install Python.Python.3.12
```

Install Flutter from `https://docs.flutter.dev/get-started/install/windows`, then open a new PowerShell:

```powershell
flutter doctor
dart --version
```

## 2. Generate Flutter Platform Folders

This repository currently contains the app source in `app/lib`. Generate Android/iOS scaffolding on a machine with Flutter installed:

```powershell
cd "C:\Major Project\bus-crowd-prediction\app"
flutter create --platforms=android,ios --org com.buscrowd .
flutter pub get
```

## 3. Configure Firebase

Create a Firebase project, then enable:

- Authentication: Anonymous and Email/Password
- Firestore Database
- Cloud Messaging

Install the CLIs and bind the app:

```powershell
dart pub global activate flutterfire_cli
npm install -g firebase-tools
firebase login
flutterfire configure
```

For Android, use package name:

```text
com.buscrowd.bus_crowd_app
```

Create conductor users in Firebase Authentication with email/password.

Suggested Firestore development rules for a pilot:

```text
rules_version = '2';
service cloud.firestore {
  match /databases/{database}/documents {
    match /live_buses/{busId} {
      allow read: if true;
      allow write: if request.auth != null;
    }
  }
}
```

For production, prefer backend-only writes with Firebase Admin and remove client writes.

## 4. Run Backend Locally

```powershell
cd "C:\Major Project\bus-crowd-prediction"
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r backend\requirements.txt
$env:CONDUCTOR_API_KEY="replace-with-a-long-random-key"
uvicorn backend.main:app --reload --port 8000
```

Android emulator app URL: `http://10.0.2.2:8000`

Physical phone URL: use your computer LAN IP, for example `http://192.168.1.12:8000`.

## 5. Deploy Backend on Render

1. Push this repository to GitHub.
2. In Render, create a new Web Service from the repository.
3. Choose Docker environment.
4. Set environment variables:

```text
CONDUCTOR_API_KEY=replace-with-the-same-long-random-key
FIREBASE_SERVICE_ACCOUNT_JSON={paste Firebase service account JSON as one line}
```

5. Deploy and copy the HTTPS URL, for example:

```text
https://bus-crowd-api.onrender.com
```

6. In the app Settings screen, paste that URL and tap "Test Connection & Save".

## 6. Run the App

```powershell
cd "C:\Major Project\bus-crowd-prediction\app"
flutter pub get
flutter run --dart-define=CONDUCTOR_API_KEY=replace-with-the-same-long-random-key
```

## 7. Build a Signed Android APK

Create a keystore:

```powershell
cd "C:\Major Project\bus-crowd-prediction\app"
keytool -genkey -v -keystore upload-keystore.jks -storetype JKS -keyalg RSA -keysize 2048 -validity 10000 -alias upload
```

Create `android/key.properties`:

```properties
storePassword=your-store-password
keyPassword=your-key-password
keyAlias=upload
storeFile=../upload-keystore.jks
```

Follow Flutter's Gradle signing setup in `android/app/build.gradle`, then build:

```powershell
flutter build apk --release --dart-define=CONDUCTOR_API_KEY=replace-with-the-same-long-random-key
```

Install on a connected Android phone:

```powershell
adb install -r build\app\outputs\flutter-apk\app-release.apk
```

## 8. End-to-End Pilot Check

1. Open the app as Conductor.
2. Sign in with the Firebase conductor account.
3. Select boarding stop, destination stop, and passenger count.
4. Tap "Issue ticket".
5. Confirm `POST /tickets` returns `201`.
6. Open the app as Passenger on another phone.
7. Search the same route.
8. Confirm the live card for `BUS-01` changes from Firestore without waiting for polling.
9. Open Bus Detail and confirm live seats plus per-stop predictions are visible.
