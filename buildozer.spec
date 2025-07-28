[app]

# (str) Title of your application
title = 网易云音乐格式转换器

# (str) Package name
package.name = ncm_converter

# (str) Package domain (needed for android/ios packaging)
package.domain = com.chengaojun.ncmconverter

# (str) Source code where the main.py live
source.dir = .

# (list) Source files to include (let empty to include all the files)
source.include_exts = py,png,jpg,kv,atlas,json

# (str) Application versioning (method 1)
version = 1.0

# (list) Application requirements
requirements = python3,kivy==2.2.0,kivymd==1.1.1,pycryptodome,plyer,android

# (str) Supported orientation (landscape, sensorLandscape, portrait or all)
orientation = portrait

# (bool) Indicate if the application should be fullscreen or not
fullscreen = 0

[buildozer]

# (int) Log level (0 = error only, 1 = info, 2 = debug (with command output))
log_level = 2

[android]

# (str) Android entry point, default is ok for Kivy-based app
#android.entrypoint = org.kivy.android.PythonActivity

# (list) Pattern to whitelist for the whole project
#android.whitelist =

# (str) Android app theme, default is ok for Kivy-based app
# android.theme = "@android:style/Theme.NoTitleBar"

# (list) Android application meta-data to set (key=value format)
#android.meta_data =

# (list) Android library project to add (will be added in the
# project.properties automatically.)
#android.library_references = @jar/my-android-library.jar

# (str) Android logcat filters to use
#android.logcat_filters = *:S python:D

# (bool) Copy library instead of making a libpymodules.so
#android.copy_libs = 1

# (str) The Android arch to build for, choices: armeabi-v7a, arm64-v8a, x86, x86_64
android.arch = arm64-v8a

# (int) overrides automatic versionCode computation (used in build.gradle)
# this is not the same as app version and should only be edited if you know what you're doing
# android.numeric_version = 1

# (bool) enables Android auto backup feature (Android API >=23)
android.allow_backup = True

# (str) XML file for custom backup rules (see official auto backup documentation)
# android.backup_rules =

# (str) If you need to insert variables into your AndroidManifest.xml file,
# you can do so with the manifestPlaceholders property.
# This property takes a map of key-value pairs.
# android.manifest_placeholders = [:]

# (bool) Skip byte compile for .py files
# android.no-byte-compile-python = False

# (str) The format used to package the app for release mode (aab or apk).
# android.release_artifact = aab

# (str) The format used to package the app for debug mode (apk or aab).
# android.debug_artifact = apk

[android.permissions]
# (list) Permissions which will be requested from the user
android.permissions = WRITE_EXTERNAL_STORAGE,READ_EXTERNAL_STORAGE,MANAGE_EXTERNAL_STORAGE

[android.gradle_dependencies]
# (list) Gradle dependencies to add
#android.gradle_dependencies =

[android.java_options]
# (str) Extra Java options to pass to the compiler
#android.java_options = -Xmx2048m

[android.ndk_api]
# (int) Android NDK API to use. This is the minimum API your app will support, it should usually match android.minapi.
#android.ndk_api = 21

[android.sdk_api]
# (int) Android SDK API to use
#android.api = 33

[android.minapi]
# (int) Minimum API your APK / AAB will support.
#android.minapi = 21

[android.gradle]
# (str) Gradle version to use
#android.gradle_version = 7.3.0

[android.ant]
# (str) Ant version to use
#android.ant_version = 1.9.4
