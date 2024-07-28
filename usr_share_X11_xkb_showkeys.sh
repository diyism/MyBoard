#!/bin/bash

if [ ! -f "hid-debug.c" ]; then
    if curl -o "hid-debug.c" "https://raw.githubusercontent.com/torvalds/linux/master/drivers/hid/hid-debug.c"; then
        echo "下载完成：hid-debug.c"
    else
        echo "下载hid-debug.c失败"
        exit 1
    fi
fi

# 定义清理函数
cleanup() {
    echo "正在停止 xkbcli 和 evtest..."
    sudo pkill -f "xkbcli interactive-evdev"
    sudo pkill -f "evtest /dev/input/event4"
    rm a.log
    exit 0
}

# 设置 trap 来捕获 SIGINT (Ctrl+C)
trap cleanup SIGINT

# 启动 xkbcli 和 evtest
sudo stdbuf -oL xkbcli interactive-evdev >> a.log 2>&1 &
sudo evtest /dev/input/event4 >> a.log 2>&1 &

# 运行 awk 脚本
tail -f a.log | awk '
    BEGIN {
        FS = "[, ]+"
    }

    function get_keycode(name) {
        if (name == "") {
            return ""
        }
        cmd = "grep \"\\[\\s\\+" name "\\(\\s\\|,\\)\" /usr/share/X11/xkb/symbols/pc /usr/share/X11/xkb/symbols/us | head -n 1 | awk \"{print \\$3}\" | xargs -I {} grep -i {} /usr/share/X11/xkb/keycodes/evdev | awk \"{sub(/;/, \\\"\\\", \\$3); print \\$3-8}\""
        cmd | getline result
        close(cmd)
        return result
    }

    function get_scanname(scancode) {
        hid_debug_file="hid-debug.c"
        target_high = "0x07"
        target_low = sprintf("0x%s", substr(scancode, length(scancode)-3))
        
        while ((getline line < hid_debug_file) > 0) {
            split(line, fields, FS)
            if (fields[2] == target_high && fields[3] == target_low) {
                gsub(/^"|"$/, "", fields[4])
                return fields[4]
            }
        }
        close(hid_debug_file)
        return ""
    }

    /keysyms/ {
        if ($5 == "keysyms") {
            keysym = $7
        } else if ($8 == "keysyms") {
            keysym = $10
        }
    }
    /MSC_SCAN/ {
        scancode = $NF
    }
    /EV_KEY/ {
        keycode = $8
        keycode_name = $9
        sub(/,/, "", keycode_name)
        sub(/\(/, "", keycode_name)
        sub(/\)/, "", keycode_name)
        if ($11 == "1") {
            action = "↓"
        } else if ($11 == "0") {
            action = "↑"
        }
        scancode_name = get_scanname(scancode)
        keysym_keycode = get_keycode(keysym)
        printf "scancode: %s(%s), keycode: %s(%s), keysym: %s(%s), action: %s\n", scancode, scancode_name, keycode, keycode_name, keysym_keycode, keysym, action
        keysym = ""
        scancode = ""
        keycode = ""
        keycode_name = ""
        action = ""
        keysym_keycode = ""
        scancode_name = ""
    }
'

# 等待子进程结束
wait
