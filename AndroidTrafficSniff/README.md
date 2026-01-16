# Environment Setup:

- Python3.8+

- Android: 4.4+

- ADB(Android Debug Bridge) : Download and install any version of ADB, and ensure that the phone has *root* access (refer to: https://developer.android.google.cn/tools/adb?hl=zh-cn)

- uiautomator2:  Utilizes the Monkey UI-testing tool to perform automated operations on Android system apps.（refer to: https://github.com/openatx/uiautomator2）

    - Installation Steps：

        -- Prepare an Android phone with *Developer Options enabled*, connect it to the computer, and ensure the device is detected by running `adb devices`
        -- Run `pip3 install -U uiautomator2`

- Weditor: A tool for recording in-app activities. By running this tool, users can connect a phone, perform custom operations, and convert their activities into executable Python code. (refer to: https://github.com/alibaba/web-editor)

    - Installation Steps：

        -- git clone https://github.com/openatx/weditor

        -- `pip3 install -e weditor`

- Networklog: A log recording tool for Android that captures real-time traffic logs generated during app execution. Each log entry includes a timestamp, network interface name, five-tuple (flow information), and the app's corresponding UID. (refer to: https://github.com/pragma-/networklog)

    - Installation Steps：

        -- Connect the phone to the computer via ADB and run `adb install network-log.apk` to install the `network-log.apk` file from the main directory.

        


## Mobile App Traffic Triggering and Labeling：
### Generate In-App Activity Execution Functions:

1. Complete the pre-installation of **weditor**. Connect your phone to the computer via USB, and after ensuring the phone is successfully connected, execute the following command in the terminal: `weditor` to open the activities recording interface.
   
2. Switch the interface to **real-time mode**, enabling the left-side panel to be fully interactive.

3. Double-click on the webpage to open the target app, then click the corresponding button to record the associated activities (the script on the right will update in real time).

4. After completing the activity recording, copy the code on the right and save it to the local directory `./apksActivity`. Name the function based on the package name (e.g., for `com.sina.weibo`, name it `com_sina_weibo`). Additionally, you can set loops or conditional statements as needed, configure time delays, and optimize the activity execution.

5. Import the function into `./executeBystr.py`, and add the corresponding package name (e.g., `com.sina.weibo`) to the relevant list in `main_sniff.py`, such as `NORMALPKGLIST`.

6. Run `python3 uiautomator2_test.py` to check if the environment is set up successfully.

   

### Device Information Collection

1. Run `adb devices` in the terminal to check the name of the currently connected mobile device (referred to as `device_sn`).

2. Run `ifconfig` or `ipconfig` in the terminal to check the host machine's current IP address (referred to as `deviceIP`).

3. Run `adb shell`, then execute `ifconfig` to check the network name the mobile device is connected to (referred to as `wlan0`).

   

### Single-App Traffic Collection

1. Execute the following command in the terminal:
    `python3 apksInstall.py --apkspath ./apkStore --device device_sn`.
    This will install the APK files located in the `./apkStore/` directory onto the mobile device.

2. Check the installed apps and manually update the app package name list `NORMALPKGLIST` in `main_sniff.py` (add or remove package names based on the target apps).

3. Run the following command:
    `python3 main_sniff.py --func normal --device device_sn --host deviceIP --net wlan0 --sample_num 30 --goaltime 300 --traffic_path ./traffic --flow2uid_path ./flow2uidJson`.
    This command will execute the `normal_sniff(arginfo)` function. Detailed descriptions of each parameter can be found within the function.

   - The function will iterate through the app list and generate traffic data files for each app based on the specified `sample_num` (number of samples).
   - It will also collect one pcap file per app, based on the `goaltime` (duration in seconds).
   - Each pcap file contains the traffic data for various app activities executed randomly within the specified `goaltime`.

4. Upon completing the traffic collection:

   - The traffic pcap files for each app will be saved in the specified `traffic_path`.

   - The corresponding app mapping for each flow in the pcap files will be saved in `flow2uid_path`.

     

### Multi-App Mixed Traffic Collection

1. Execute the following command in the terminal:
    `python3 apksInstall.py --apkspath ./apkStore --device device_sn`.
    This will install the APK files located in the `./apkStore/` directory onto the mobile device.
2. Check the installed apps and manually update the app package name lists in `main_sniff.py`. Specifically:
   - Use `FOREPKGLIST` for the foreground app list.
   - Use `BACKPKGLIST` for the background app list.
     Add or remove package names based on target requirements.
3. Run the following command:
    `python3 main_sniff.py --func multi --device device_sn --host deviceIP --net wlan0 --sample_num 15 --goaltime 300 --traffic_path ./traffic_multi --flow2uid_path ./flow2uidJson_multi`.
    Detailed descriptions of each parameter can be found in the function. This command will execute the `multi_sniff(arginfo)` function.
   - The function iterates through both the foreground app list and the background app list.
   - Background apps are started and suspended, while foreground app activities are executed.
   - Traffic is collected into a single pcap file, which contains activities from one background app and random activities from multiple foreground apps during the specified `goaltime` duration.
4. Once traffic collection is completed:
   - The pcap files for each app's traffic are stored in the specified `traffic_path`.
   - The mapping of each flow in the pcap files to the corresponding app is saved in `flow2uid_path`.



### Fine-Grained Multi-Action Traffic Collection

1. Execute the following command in the terminal:
    `python3 apksInstall.py --apkspath ./apkStore --device device_sn`
    This will install the APK files located in the `./apkStore/` directory onto the mobile device.
2. Check the installed apps and manually update the app package name list `ACKPKGLIST` in `main_sniff.py`.
    Add or remove package names based on target requirements. Each app in the list is expected to have 7 independent activity functions defined.
3. Run the following command:
    `python3 main_sniff.py --func activity --device device_sn --host deviceIP --net wlan0 --sample_num 12 --goaltime 300 --traffic_path ./traffic_act --flow2uid_path ./flow2uidJson_act`
    This command will execute the `act_sniff(arginfo)` function. Detailed descriptions of the parameters are available within the function.
   - The function iterates through the 7 independent activities of each app in the list.
   - For each activity of an app, a pcap file is generated, capturing the traffic for that single activity over the specified `goaltime` duration.
   - Each activity will collect `sample_num` pcap files.
4. Once traffic collection is completed:
   - The pcap files corresponding to each app’s traffic are saved in the specified `traffic_path`.

   - The mapping of each flow in the pcap files to the corresponding app is saved in `flow2uid_path`.
