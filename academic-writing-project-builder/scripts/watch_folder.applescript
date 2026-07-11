-- watch_folder.applescript
-- AppleScript Folder Action 版本：md 文件夹变化时触发 convert.sh
-- 保存到 ~/Library/Scripts/Folder Action Scripts/，然后右键 md 文件夹 → 附加文件夹动作
on adding folder items to theAttachedFolder after receiving theNewItems
    repeat with anItem in theNewItems
        set ext to do shell script "basename " & quoted form of POSIX path of anItem & " | sed 's/.*\\.//'"
        if ext is "md" then
            do shell script "cd " & quoted form of POSIX path of theAttachedFolder & " && bash script/convert.sh"
        end if
    end repeat
end adding folder items to
