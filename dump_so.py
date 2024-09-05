import sys
import frida
import sys
import os


def fix_so(arch, origin_so_name, so_name, base, size):
    if arch == "arm":
        os.system("adb push android/SoFixer32 /data/local/tmp/SoFixer")
    elif arch == "arm64":
        os.system("adb push android/SoFixer64 /data/local/tmp/SoFixer")
    os.system("adb shell chmod +x /data/local/tmp/SoFixer")
    os.system("adb push " + so_name + " /data/local/tmp/" + so_name)
    print("adb shell /data/local/tmp/SoFixer -m " + base + " -s /data/local/tmp/" + so_name + " -o /data/local/tmp/" + so_name + ".fix.so")
    os.system("adb shell /data/local/tmp/SoFixer -m " + base + " -s /data/local/tmp/" + so_name + " -o /data/local/tmp/" + so_name + ".fix.so")
    os.system("adb pull /data/local/tmp/" + so_name + ".fix.so " + origin_so_name + "_" + base + "_" + str(size) + "_fix.so")
    os.system("adb shell rm /data/local/tmp/" + so_name)
    os.system("adb shell rm /data/local/tmp/" + so_name + ".fix.so")
    os.system("adb shell rm /data/local/tmp/SoFixer")

    return origin_so_name + "_" + base + "_" + str(size) + "_fix.so"


def read_frida_js_source():
    with open("dump_so.js", "r") as f:
        return f.read()

def on_message(message, data):
    if data:
        chunk_index = message['payload']['chunk_index']
        total_chunks = message['payload']['total_chunks']
        print(f"Receiving chunk {chunk_index + 1}/{total_chunks}")
        with open(dump_so_name, "ab") as f:
            f.write(data)  # 逐块写入文件
    else:
        if message['payload']['status'] == "complete":
            print("Dump complete.")

if __name__ == "__main__":
    device: frida.core.Device = frida.get_usb_device()
    pid = device.get_frontmost_application().pid
    session: frida.core.Session = device.attach(pid)
    script = session.create_script(read_frida_js_source())
    script.on('message', on_message)
    script.load()

    if len(sys.argv) < 2:
        allmodule = script.exports_sync.allmodule()
        for module in allmodule:
            print(module["name"])
    else:
        origin_so_name = sys.argv[1]
        module_info = script.exports_sync.findmodule(origin_so_name)
        print(module_info)
        base = module_info["base"]
        size = module_info["size"]
        dump_so_name = origin_so_name + ".dump.so"

        script.exports_sync.dumpmodule(origin_so_name)

        arch = script.exports_sync.arch()
        fix_so_name = fix_so(arch, origin_so_name, dump_so_name, base, size)
        
        print(fix_so_name)
        os.remove(dump_so_name)
