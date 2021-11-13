#!/bin/python3

import colorgram
from configparser import ConfigParser
import yaml
import os
from PIL import Image, ImageDraw, ImageFont, ImageOps, ImageEnhance
from colour import Color
import json


class ThemeSetter:
    def __init__(self, palette: dict):
        self.palette = dict()
        for k in palette.keys():
            self.palette[k] = Color(palette[k])

    def alacritty(self, configPath=os.path.expanduser('~/.config/alacritty/alacritty.yml')) -> None:
        config = None
        if os.path.isfile(configPath):
            config = yaml.load(
                open(configPath, 'r'), Loader=yaml.FullLoader)
            config['colors']['primary']['background'] = self.palette['background'].hex
            config['colors']['primary']['foreground'] = self.palette['foreground'].hex
        open(os.path.expanduser(configPath), 'w').write(yaml.dump(config))
        pass

    def i3(self, configPath=os.path.expanduser('~/.i3/config')) -> None:
        configFile = open(configPath, 'r').read()
        configFileLines = configFile.split('\n')
        finalConfigLines = []

        for l in configFileLines:
            if not l.strip().startswith('client.'):
                finalConfigLines.append(l)

        finalConfigLines.append("client.focused\t" + self.palette['background'].hex + '55 ' +
                                self.palette['background'].hex + ' ' + self.palette['foreground'].hex + ' ' + self.palette['background'].hex + '55')
        finalConfigLines.append("client.focused_inactive\t" + self.palette['background'].hex + '33 ' +
                                self.palette['background'].hex + '33 ' + self.palette['foreground'].hex + '33 ' + self.palette['background'].hex + '33')
        finalConfigLines.append("client.unfocused\t" + self.palette['background'].hex + '33 ' +
                                self.palette['background'].hex + '33 ' + self.palette['foreground'].hex + '33 ' + self.palette['background'].hex + '33')
        finalConfigLines.append(
            "client.background\t" + self.palette['background'].hex)

        open(configPath, 'w').write("\n".join(finalConfigLines))

    def vscode(self, configPath=os.path.expanduser('~/.config/Code/User/settings.json')):
        settingsContent = "".join([c.strip()
                                  for c in open(configPath, 'r').readlines()])
        settings = json.loads(settingsContent, strict=False)

        regular = self.palette['background'].hex
        accent = self.palette['accent'].hex
        primaryDark = Color(rgb=self.adjust_lightness(
            self.palette['primary'].hex, 0.36)).hex
        primaryDarkest = Color(rgb=self.adjust_lightness(
            self.palette['primary'].hex, 0.31)).hex
        dark = Color(rgb=self.adjust_lightness(regular, 0.8)).hex
        darkest = Color(rgb=self.adjust_lightness(regular, 0.8)).hex
        light = Color(rgb=self.adjust_lightness(regular, 1.7)).hex
        foreground = self.palette['foreground'].hex

        settings['workbench.colorCustomizations'] = {
            "menu.background": regular,
            "badge.background": accent,
            "input.background": regular,
            "panel.background": regular,
            "banner.background": regular,
            "button.background": regular,
            "editor.background": regular,
            "sideBar.background": dark,
            "minimap.background": regular,
            "tab.hoverBackground": primaryDarkest,
            "terminal.background": regular,
            "breadcrumb.background": regular,
            "editor.selectionBackground": light,
            "list.inactiveSelectionBackground": regular,
            "tab.inactiveBackground": darkest,
            "editorGroupHeader.tabsBackground": regular,
            "tab.activeBackground": regular,
            "sideBarSectionHeader.background": regular,
            "activityBar.background": regular,
            "editorWidget.background": dark,
            "editor.lineHighlightBackground": light,
            "activityBar.activeBackground": primaryDark,
            "foreground": foreground,
            "focusBorder": foreground,
            "icon.foreground": accent,
            "statusBar.background": primaryDark,
            "titleBar.activeBackground": primaryDark
        }

        open(configPath, 'w').write(json.dumps(settings))

    def setIniFile(self, configPath, section, map):
        parser = ConfigParser()
        parser.read(configPath)
        for key in map:
            parser.set(section, key, self.palette[map[key]].hex)
        with open(configPath, 'w') as configFile:
            parser.write(configFile)

    def polybar(self, configPath=os.path.expanduser('~/.config/polybar/colors.ini'), section='color', map={'background': 'background', 'foreground': 'foreground'}):
        self.setIniFile(configPath, section, map)

    def adjust_lightness(self, color, amount=0.5):
        import matplotlib.colors as mc
        import colorsys
        try:
            c = mc.cnames[color]
        except:
            c = color
        c = colorsys.rgb_to_hls(*mc.to_rgb(c))
        return colorsys.hls_to_rgb(c[0], max(0, min(1, amount * c[1])), c[2])

    # def savePalette(self) -> None:
    #     paletteImg = Image.new('RGB', (1920, 1080))
    #     font = ImageFont.truetype('./montserrat.ttf', 64)
    #     hexColors = [c.hex for c in self.palette]

    #     draw = ImageDraw.Draw(paletteImg)
    #     hexOthers = [c.hex for c in self.palette['others']]
    #     for i in range(len(hexColors)):
    #         draw.rectangle(((1920 / len(hexColors))*i, 0, (1920 / len(hexColors)) *
    #                         (i+1), 1080), fill=hexColors[i], outline=None)
    #         drawText = hexColors[i]
    #         if hexColors[i] == self.palette['background'].hex:
    #             drawText += ' (background)'
    #         elif hexColors[i] == self.palette['foreground'].hex:
    #             drawText += ' (foreground)'
    #         elif hexColors[i] in hexOthers:
    #             drawText += ' (other)'

    #         frame = Image.new('L', font.getsize(drawText))
    #         drawFrame = ImageDraw.Draw(frame)
    #         drawFrame.text((0, 0),
    #                        drawText, fill='#fff', font=font)
    #         w = frame.rotate(-90, expand=True)
    #         paletteImg.paste(ImageOps.colorize(
    #             w, (0, 0, 0), '#fff'), (((1920 // len(hexColors))*(i+1)) - (1920 // len(hexColors)) // 2 - (font.getsize(drawText)[1]//2), 20), w)

    #     paletteImg.save('palette.png', 'PNG')


if __name__ == "__main__":
    palette = json.load(open('palette.json', 'r'))
    theme = ThemeSetter(palette)
    theme.alacritty()
    theme.i3()
    theme.vscode()
    theme.polybar(os.path.expanduser('~/.config/polybar/forest/colors.ini'))
