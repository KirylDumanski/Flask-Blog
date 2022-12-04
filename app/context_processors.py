from slugify import slugify

menu = [{"name": "Main page", "url": "post/list"},
        {"name": "Add post", "url": "post/add"},
        {"name": "Feedback", "url": "feedback"}
        ]


def inject_mainmenu():
    return dict(menu=menu)
