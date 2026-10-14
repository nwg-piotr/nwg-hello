hl.config({
  misc = {
    disable_hyprland_logo = true,
    disable_splash_rendering = true,
    disable_xdg_env_checks = true,
    disable_scale_notification = true,
  },
  animations = { enabled = false },
})

local greeter_cmd = "nwg-hello 2> /dev/null; hyprctl dispatch exit"
hl.on("hyprland.start", function()
  hl.exec_cmd(greeter_cmd)
end)
