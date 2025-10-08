import subprocess
import os
import argparse
#给定安装包路径，安装路径下的所有安装包
def install(apkspath):
    allapks = os.listdir(apkpath)
    i = 0
    for apkname in allapks:
        i += 1
        print(f"processing appname {apkname}, left: {len(allapks) - i + 1}")
        apkpath = os.path.join(apkspath,apkname)
        installcmd = ['adb','-s', device, 'install', apkpath]
        adbProcess = subprocess.Popen(installcmd, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        ret = adbProcess.communicate()
    return ret
def get_parser():
    parser = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument('--apkspath', type=str, default=r'./apkStore')
    parser.add_argument('--device', type=str, default="8A4X0LJJP", 
                        help="adb device name  you want to install apks, you can get it by running command:'adb device'")
    return parser
if __name__ == "__main__":
    """ Example:
    device = "deviceIP:port"
    device = "XXXX"
    """
    args = get_parser().parse_args()
    device = args.device
    install(apkspath=args.apkspath)
   