"""Renders templates with Jinja and writes to files in /docs."""
from pathlib import Path
from jinja2 import Template, Environment, FileSystemLoader
from mistune import markdown

def compile_templates(env, templates_dir, metadata):
    output_dir = Path('docs')
    for template_file in templates_dir.iterdir():
        name = template_file.name
        if not 'base' in name:
            template = env.get_template(name)
            try:
                (d, n) = name.split('_')
                print(f'Compiling {d}/{n}...')
                with open(output_dir / d / n, 'w+') as f:
                    if name == 'blog_index.html':
                        f.write(template.render(posts=metadata))
                    else:
                        f.write(template.render())
            except ValueError:
                print(f'Compiling {name}...')
                with open(output_dir / name, 'w+') as f:
                    f.write(template.render())
                    
    for blogpost in metadata:
        print(f'Compiling {blogpost.file}...')
        with open(output_dir / 'blog' / blogpost.file, 'w+') as f:
            f.write(blogpost.render_template(env))

def create_blog_templates(templates_dir):
    metadata = []
    posts_dir = Path('posts')
    for post_file in posts_dir.iterdir():
        print(f'Adding {post_file.name} to posts...')
        metadata.append(PostMetadata(post_file.name[:-3]))
        with open(post_file, 'r') as f:
            # Grab the post title to use in /blog/index.html and <title> tags.
            metadata[-1].title = f.readline().rstrip()[2:]
            # Return to top and and entire file contents.
            f.seek(0)
            metadata[-1].content = markdown(f.read())
    return metadata

class PostMetadata:
    def __init__(self, filename):
        (self.date, self.file) = filename.split('_')
        self.file += '.html'
        self.title = ''
        self.content = ''

    def template(self):
        return (
            f'{{% extends "blogpost-base.html" %}}\n'
            f'{{% block title %}}{self.title}{{% endblock %}}\n'
            f'{{% block post %}}\n'
            f'{self.content}\n'
            f'{{% endblock %}}'
        )

    def render_template(self, env):
        return env.from_string(self.template()).render()

if __name__ == '__main__':
    # Load directories to read from/write to.
    templates_dir = Path('templates')
    # Load templates into Jinja (for template inheritance).
    env = Environment(loader=FileSystemLoader('templates'))

    # Create templates for blog posts and get metadata for each.
    metadata = create_blog_templates(templates_dir)
    # Write all templates to /docs
    compile_templates(env, templates_dir, metadata)
