# DataRW Mobile App Build Instructions

## 📱 APK Build Guide

### Prerequisites
1. **Node.js 16+** installed
2. **React Native CLI** installed globally: `npm install -g @react-native-community/cli`
3. **Android Studio** with Android SDK
4. **Java JDK 11** or higher

### Build Steps

1. **Navigate to mobile app directory:**
   ```bash
   cd /app/mobile-app
   ```

2. **Install dependencies:**
   ```bash
   yarn install
   ```

3. **Run the build script:**
   ```bash
   chmod +x build-apk.sh
   ./build-apk.sh
   ```

4. **Build the APK (requires Android SDK):**
   ```bash
   cd android
   ./gradlew assembleRelease
   ```

5. **Find the APK:**
   ```
   android/app/build/outputs/apk/release/app-release.apk
   ```

### App Configuration

**Before building, update the API endpoint in:**
- `src/services/ApiService.js` - Change `BASE_URL` to your production URL

**Key Features Built:**
- ✅ Offline-first architecture with SQLite
- ✅ Automatic sync when online
- ✅ Enumerator authentication system
- ✅ Multi-question type support
- ✅ Progress tracking and validation
- ✅ Secure local data storage

### App Details
- **Package Name:** com.datarw.survey  
- **Version:** 1.0.0
- **Min Android:** 5.0 (API 21)
- **Target Android:** 14 (API 34)
- **Estimated Size:** ~25 MB

### Deployment
1. Copy built APK to `/app/frontend/public/downloads/`
2. Update download link in landing page
3. Test download functionality
4. Optionally publish to Google Play Store

### Troubleshooting

**Common Issues:**
- **Gradle Build Failed:** Ensure Android SDK and build tools are installed
- **Metro Bundle Error:** Clear cache with `npx react-native start --reset-cache`
- **Dependency Issues:** Delete node_modules and run `yarn install`

**For Production:**
- Generate signed release keystore
- Update app signing configuration
- Test on multiple Android devices
- Configure ProGuard for code obfuscation