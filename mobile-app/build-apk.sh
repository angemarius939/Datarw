#!/bin/bash

# DataRW Mobile App APK Build Script
# This script builds the React Native app into an APK file

set -e

echo "🚀 Building DataRW Mobile App APK..."

# Check if we're in the right directory
if [ ! -f "package.json" ]; then
    echo "❌ Error: package.json not found. Run this script from the mobile-app directory."
    exit 1
fi

# Create build directories
mkdir -p build
mkdir -p android/app/src/main/assets

echo "📦 Installing dependencies..."
# Install Node.js dependencies
if command -v yarn &> /dev/null; then
    yarn install
else
    npm install
fi

echo "🔧 Creating React Native bundle..."
# Create the React Native bundle
npx react-native bundle \
    --platform android \
    --dev false \
    --entry-file index.js \
    --bundle-output android/app/src/main/assets/index.android.bundle \
    --assets-dest android/app/src/main/res/

echo "📱 Creating Android project structure..."
# Create necessary Android files if they don't exist

# Create MainActivity.java
mkdir -p android/app/src/main/java/com/datarw/survey
cat > android/app/src/main/java/com/datarw/survey/MainActivity.java << 'EOF'
package com.datarw.survey;

import com.facebook.react.ReactActivity;
import com.facebook.react.ReactActivityDelegate;
import com.facebook.react.defaults.DefaultNewArchitectureEntryPoint;
import com.facebook.react.defaults.DefaultReactActivityDelegate;

public class MainActivity extends ReactActivity {

  /**
   * Returns the name of the main component registered from JavaScript. This is used to schedule
   * rendering of the component.
   */
  @Override
  protected String getMainComponentName() {
    return "DataRWMobile";
  }

  /**
   * Returns the instance of the {@link ReactActivityDelegate}. Here we use a util class {@link
   * DefaultReactActivityDelegate} which allows you to easily enable Fabric and Concurrent React
   * (aka React 18) with two boolean flags.
   */
  @Override
  protected ReactActivityDelegate createReactActivityDelegate() {
    return new DefaultReactActivityDelegate(
        this,
        getMainComponentName(),
        // If you opted-in for the New Architecture, we enable the Fabric Renderer.
        DefaultNewArchitectureEntryPoint.getFabricEnabled());
  }
}
EOF

# Create MainApplication.java
cat > android/app/src/main/java/com/datarw/survey/MainApplication.java << 'EOF'
package com.datarw.survey;

import android.app.Application;
import com.facebook.react.ReactApplication;
import com.facebook.react.ReactNativeHost;
import com.facebook.react.ReactPackage;
import com.facebook.react.config.ReactFeatureFlags;
import com.facebook.react.defaults.DefaultNewArchitectureEntryPoint;
import com.facebook.react.defaults.DefaultReactNativeHost;
import com.facebook.soloader.SoLoader;
import java.util.List;

public class MainApplication extends Application implements ReactApplication {

  private final ReactNativeHost mReactNativeHost =
      new DefaultReactNativeHost(this) {
        @Override
        public boolean getUseDeveloperSupport() {
          return BuildConfig.DEBUG;
        }

        @Override
        protected List<ReactPackage> getPackages() {
          @SuppressWarnings("UnnecessaryLocalVariable")
          List<ReactPackage> packages = new PackageList(this).getPackages();
          return packages;
        }

        @Override
        protected String getJSMainModuleName() {
          return "index";
        }

        @Override
        protected boolean isNewArchEnabled() {
          return BuildConfig.IS_NEW_ARCHITECTURE_ENABLED;
        }

        @Override
        protected Boolean isHermesEnabled() {
          return BuildConfig.IS_HERMES_ENABLED;
        }
      };

  @Override
  public ReactNativeHost getReactNativeHost() {
    return mReactNativeHost;
  }

  @Override
  public void onCreate() {
    super.onCreate();
    SoLoader.init(this, /* native exopackage */ false);
    if (BuildConfig.IS_NEW_ARCHITECTURE_ENABLED) {
      // If you opted-in for the New Architecture, we load the native entry point for this app.
      DefaultNewArchitectureEntryPoint.load();
    }
    ReactFeatureFlags.useTurboModules = BuildConfig.IS_NEW_ARCHITECTURE_ENABLED;
  }
}
EOF

echo "🎨 Creating app icons and resources..."
# Create drawable and mipmap directories
mkdir -p android/app/src/main/res/drawable
mkdir -p android/app/src/main/res/mipmap-hdpi
mkdir -p android/app/src/main/res/mipmap-mdpi
mkdir -p android/app/src/main/res/mipmap-xhdpi
mkdir -p android/app/src/main/res/mipmap-xxhdpi
mkdir -p android/app/src/main/res/mipmap-xxxhdpi
mkdir -p android/app/src/main/res/values

# Create app theme
cat > android/app/src/main/res/values/styles.xml << 'EOF'
<resources>
    <style name="AppTheme" parent="Theme.AppCompat.DayNight.NoActionBar">
        <item name="android:editTextBackground">@android:drawable/edit_text</item>
        <item name="android:textColor">#000000</item>
        <item name="android:statusBarColor">@android:color/transparent</item>
        <item name="android:navigationBarColor">@android:color/transparent</item>
        <item name="android:windowTranslucentStatus">false</item>
        <item name="android:windowTranslucentNavigation">false</item>
        <item name="android:windowDrawsSystemBarBackgrounds">true</item>
    </style>
</resources>
EOF

# Create simple launcher icons (placeholder)
cat > android/app/src/main/res/drawable/launch_screen.xml << 'EOF'
<?xml version="1.0" encoding="utf-8"?>
<layer-list xmlns:android="http://schemas.android.com/apk/res/android">
    <item android:drawable="@color/primary_dark" />
    <item
        android:width="144dp"
        android:height="144dp"
        android:drawable="@mipmap/ic_launcher"
        android:gravity="center" />
</layer-list>
EOF

cat > android/app/src/main/res/values/colors.xml << 'EOF'
<resources>
    <color name="primary_dark">#2563eb</color>
    <color name="white">#FFFFFF</color>
</resources>
EOF

echo "📋 Creating APK manifest..."
# Create a simple APK info file
cat > build/apk-info.json << EOF
{
  "app_name": "DataRW Survey",
  "version": "1.0.0",
  "package_name": "com.datarw.survey",
  "build_date": "$(date -u +%Y-%m-%dT%H:%M:%SZ)",
  "features": [
    "Offline survey data collection",
    "Automatic sync when online",
    "Enumerator authentication",
    "Multiple question types support",
    "Progress tracking"
  ],
  "permissions": [
    "INTERNET",
    "ACCESS_NETWORK_STATE", 
    "WAKE_LOCK",
    "WRITE_EXTERNAL_STORAGE",
    "READ_EXTERNAL_STORAGE"
  ]
}
EOF

echo "✅ APK build preparation completed!"
echo ""
echo "📱 APK Information:"
echo "   • App Name: DataRW Survey"
echo "   • Version: 1.0.0"
echo "   • Package: com.datarw.survey"
echo "   • Build Date: $(date)"
echo ""
echo "🔧 To complete the APK build, you need:"
echo "   1. Android SDK installed"
echo "   2. Java JDK 11 or higher"
echo "   3. Run: cd android && ./gradlew assembleRelease"
echo ""
echo "📦 The APK will be generated at:"
echo "   android/app/build/outputs/apk/release/app-release.apk"
echo ""
echo "🎉 Build script completed successfully!"