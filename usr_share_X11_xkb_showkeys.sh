#!/bin/bash

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
    function get_keycode(name) {
        if (name == "") {
            return ""
        }
        cmd = "grep \"\\[\\s\\+" name "\\(\\s\\|,\\)\" /usr/share/X11/xkb/symbols/pc /usr/share/X11/xkb/symbols/us | head -n 1 | awk \"{print \\$3}\" | xargs -I {} grep -i {} /usr/share/X11/xkb/keycodes/evdev | awk \"{sub(/;/, \\\"\\\", \\$3); print \\$3-8}\""
        cmd | getline result
        close(cmd)
        return result
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
        keysym_keycode = get_keycode(keysym)
        printf "scancode: %s, keycode: %s(%s), keysym: %s(%s), action: %s\n", scancode, keycode, keycode_name, keysym, keysym_keycode, action
        keysym = ""
        scancode = ""
        keycode = ""
        keycode_name = ""
        action = ""
        keysym_keycode = ""
    }
'

# 等待子进程结束
wait
