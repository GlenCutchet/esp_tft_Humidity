from ili9XXX import ili9488g

from ft6x36 import ft6x36

disp=ili9488g()

touch=ft6x36(0, 21, 22, 10000)

scr=lv.obj()

btn=lv.btn(scr)

btn.center()

label=lv.label(btn)

label.set_text('Button')

lv.scr_load(scr)