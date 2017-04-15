#!/usr/bin/python3

from virtberry_module_management import *
import json
from flask import current_app

def get_url(entry):
    if not entry.get("parent"):
        # we are in the first stage we need a absolute url
        if entry.get("absolute_url", "") == "":
            # we need a exception here
            print("Error")
            exit(1)
        else:
            url = {}
            url.setdefault("absolute_url", entry.get("absolute_url"))
            return url
    else:
        # we can use a relative url, but we like a absolute url more
        if not entry.get("absolute_url", "") == "":
            # if we have a absolute url we use this
            url = {}
            url.setdefault("absolute_url", entry.get("absolute_url"))
            return url
        else:
            # we need the relative url
            if entry.get("relative_url", "") == "":
                # absolute and relative_url are empty. not good
                print("Error")
                exit(1)
            else:
                url = {}
                url.setdefault("relative_url", entry.get("relative_url"))
                return url


def build_menu_item(entry):
    menu_item = {}
    keys = ["index", "displayname", "type"]
    for key in keys:
        menu_item.setdefault(key, entry.get(key))

    menu_item.update(get_url(entry))

    if entry.get("type") == "dropdown":
        menu_item.setdefault("child", [])

    return menu_item


def build_menu_item_placeholder(index):
    placeholder= {}
    placeholder.setdefault("index", index)
    placeholder.setdefault("type", "placeholder")
    placeholder.setdefault("child", [])
    return placeholder



def add_to_menu(menu, item, parent, stage):
    if stage == len(parent) +1 :
        # we are in the last stage where we have to add the item
        #check for placeholders
        for entry in menu:
            if entry.get("index") == item.get("index"):
                # The place holder can have childs, so we need to add these childs to the item
                child = {}
                child.setdefault("child", entry.get("child"))
                item.update(child)
                entry.update(item)
                return
        # the entry seem to be not in the list
        menu.append(item)
        return
    else:
        print("get here")
        # the menu is empty
        if len(menu) == 0:
            menu.append(build_menu_item_placeholder(parent[ stage - 1 ]))
            entry = menu[-1]
            menu = entry.get("child")
        else:
            for entry in menu:
                if entry.get("index") == parent[ stage - 1 ]:
                    menu = entry.get("child")
                    print("gethere3")
                else:
                    menu.append(build_menu_item_placeholder(parent[ stage - 1 ]))
                    print("get here2")
                    print(build_menu_item_placeholder(parent[ stage - 1 ]))
                    print(menu)
                    entry = menu[-1]
                    print(entry)
                    menu = entry.get("child")
        add_to_menu(menu, item, parent, stage +1)

def check_for_placeholder(menu):
    for entry in menu:
        if entry.get("type") == "placeholder":
            return 1
        else:
            if not entry.get("child"):
                # the entry is not from type placeholder and the child is empty
                pass
            else:
                if check_for_placeholder(entry.get("child")) == 1:
                    return 1
    # if we get here the whole menu is checked
    return 0

def from_relative_to_absolute_url(menu, url):
    for item in menu:
        if "relative_url" in item:
            absolute_url = ""
            absolute_url += url
            absolute_url += item.get("relative_url")
            print(absolute_url)
            item.setdefault("absolute_url", absolute_url)
            item.pop("relative_url")
            from_relative_to_absolute_url(item.get("child", []), absolute_url)

        if "absolute_url" in item:
            from_relative_to_absolute_url(item.get("child", []), item.get("absolute_url"))

    return

def build_menu():
    for module in get_enabled_modules():
        the_module = virtberry_module(module)
        menu = the_module.get_attributes("menu")
        real_menu = []
        for entry in menu:
            add_to_menu(real_menu,build_menu_item(entry),entry.get("parent"), 1)

        if check_for_placeholder(real_menu) == 1:
            print("placeholders in menu")
            exit(1)

        from_relative_to_absolute_url(real_menu,"")
        return real_menu

def menu_context_processor():
    return dict(menu=current_app.menu.the_menu)

class Menu():
    def __init__(self):
        self.the_menu = build_menu()
        print(json.dumps(self.the_menu))

    def init_app(self, app):
         app.menu = self
         app.context_processor(menu_context_processor)
