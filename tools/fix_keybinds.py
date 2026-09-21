#!/usr/bin/env python3
"""Re-apply the pack's keybinds to a version's options.txt.

Minecraft writes the whole options file from memory when it exits, so if the game is running when these
values are edited (or when the pack is exported), the edits are silently overwritten by the old keybinds.
This script exists to put them back - run it with the game closed:

    python3 tools/fix_keybinds.py "/mnt/d/666/新建文件夹/.minecraft/versions/钢与血(Steel & Blood)"
    python3 tools/fix_keybinds.py <版本目录> --check      # 只检查，不修改

The list below is the pack's key layout. Everything in it moves a binding off a key that something more
important already needed (voice chat push-to-talk, Superb Warfare's melee, its fire-mode switch).
"""
import pathlib
import sys

# action -> (key, why)
WANTED = {
    # --- 本包新增的机制 ---
    "key_key.sbw_gore.self_shot": ("key.keyboard.z", "把枪口转向自己（按住 Z → 左键）"),
    "key_key.sbw_gore.clear_jam": ("key.keyboard.n", "排除枪械故障"),
    "key_key.sbw_gore.inspect": ("key.keyboard.semicolon", "检视武器"),
    # --- 让路给上面三个而挪走的 ---
    "key_key.superbwarfare.fire_mode": ("key.keyboard.y", "切换射击模式（原 N）"),
    "key_key.disable_voice_chat": ("key.keyboard.f7", "关闭语音聊天（原 N，再让开 - 给小地图缩放）"),
    "key_key.travelersbackpack.cycle_tool": ("key.keyboard.bracketleft", "切换背包工具（原 Z）"),
    # --- 三个模组抢同一个键，按"谁更常用"重新分配：M 归地图、H 归身体部位、U 归换肩 ---
    "key_key.mute_microphone": ("key.keyboard.insert", "麦克风静音（原 M，让给 FTB 地图）"),
    "key_key.superbwarfare.toggle_tactical_map": ("key.keyboard.home", "卓越前线战术地图（原 M，与 FTB 地图重复）"),
    "key_key.hide_icons": ("key.keyboard.comma", "隐藏任务图标（原 H，让给身体部位面板）"),
    "key_key.tctcore.tc_tcore_key": ("key.keyboard.backslash", "TCT 核心按键（原 H，同上）"),
    "key_key.corpse.death_history": ("key.keyboard.end", "死亡记录（原 U，让给越肩换肩）"),
    "key_key.superbwarfare.disconnect_towing": ("key.keyboard.f8", "断开载具牵引（原 Y，让给切换射击模式）"),
}


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        return 2
    version_dir = pathlib.Path(sys.argv[1])
    check_only = "--check" in sys.argv
    options = version_dir / "options.txt"
    if not options.exists():
        print(f"找不到 {options}")
        return 2

    text = options.read_text(encoding="utf-8", errors="surrogateescape")
    changed, problems = 0, []
    for action, (key, why) in WANTED.items():
        current = None
        for line in text.splitlines():
            if line.startswith(action + ":"):
                current = line.split(":", 1)[1].strip()
                break
        if current == key:
            print(f"  正确  {action} = {key}")
            continue
        print(f"  {'需要修正' if current else '缺失键位'}  {action}: {current or '(无)'} → {key}   ({why})")
        if check_only:
            problems.append(action)
            continue
        if current is None:
            text = text.rstrip("\n") + f"\n{action}:{key}\n"
        else:
            text = text.replace(f"{action}:{current}", f"{action}:{key}")
        changed += 1

    if check_only:
        print("\n检查完成：" + ("全部正确" if not problems else f"{len(problems)} 项需要修正（用不带 --check 的方式运行）"))
        return 1 if problems else 0

    if changed:
        options.write_text(text, encoding="utf-8", errors="surrogateescape")
        print(f"\n已修正 {changed} 项 —— 注意：游戏必须处于关闭状态，否则退出时会被覆盖回去。")
    else:
        print("\n无需修改。")
    return 0


if __name__ == "__main__":
    sys.exit(main())
