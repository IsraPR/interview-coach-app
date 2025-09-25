from pathlib import Path
from typing import Any, Dict, Optional

import frontmatter
from jinja2 import (
    Environment,
    FileSystemLoader,
    StrictUndefined,
    TemplateError,
    meta,
)

BASE_DIR = Path(__file__).resolve().parent.parent


class PromptManager:
    """
    Manages loading and rendering Jinja2 templates with YAML frontmatter.

    An instance of this class is configured with a specific template directory.
    It creates and holds a Jinja2 Environment, providing methods to render
    prompts or inspect template metadata.
    """

    def __init__(
        self,
        template_dir: str | None = None,
        default_file_extension: str = "j2",
    ):
        """
        Initializes the PromptManager.

        Args:
            template_dir: The relative or absolute path to the template directory.
            default_file_extension: The default file extension for templates (e.g., 'j2', 'txt').
        """
        if template_dir is None:
            template_dir: Path = BASE_DIR / "prompts" / "templates"

        self.template_dir = Path(template_dir)
        self.default_file_extension = default_file_extension

        if not self.template_dir.is_dir():
            raise FileNotFoundError(
                f"The template directory does not exist: {self.template_dir}"
            )

        self._env: Environment = Environment(
            loader=FileSystemLoader(str(self.template_dir)),
            undefined=StrictUndefined,
        )

    def get_prompt(
        self,
        template_name: str,
        file_extension: Optional[str] = None,
        **render_kwargs: Any,
    ) -> str:
        """
        Loads a template, parses its frontmatter, and renders its content.

        Args:
            template_name: The name of the template file (without extension).
            file_extension: Override the default file extension for this call.
            **render_kwargs: Key-value pairs to pass to the template for rendering.

        Returns:
            The rendered string prompt.
        """
        extension = (
            file_extension
            if file_extension is not None
            else self.default_file_extension
        )
        template_path = f"{template_name}.{extension}"

        # get_source -> (source, filename, uptodate)
        source, _, _ = self._env.loader.get_source(self._env, template_path)
        post = frontmatter.loads(source)
        jinja_template = self._env.from_string(post.content)

        try:
            return jinja_template.render(**render_kwargs)
        except TemplateError as e:
            raise ValueError(
                f"Error rendering template '{template_path}': {e}"
            ) from e

    def render_template(
        self,
        source: str,
        **render_kwargs: Any,
    ):
        post = frontmatter.loads(source)
        jinja_template = self._env.from_string(post.content)
        try:
            return jinja_template.render(**render_kwargs)
        except TemplateError as e:
            raise ValueError(f"Error rendering source template: {e}") from e

    def get_template_info(
        self, template_name: str, file_extension: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Parses a template to extract its metadata and declared variables.

        Args:
            template_name: The name of the template file (without extension).
            file_extension: Override the default file extension for this call.

        Returns:
            A dictionary containing template metadata.
        """
        extension = (
            file_extension
            if file_extension is not None
            else self.default_file_extension
        )
        template_path = f"{template_name}.{extension}"

        source, _, _ = self._env.loader.get_source(self._env, template_path)
        post = frontmatter.loads(source)
        ast = self._env.parse(post.content)
        variables = meta.find_undeclared_variables(ast)

        return {
            "name": template_name,
            "description": post.metadata.get(
                "description", "No description provided"
            ),
            "author": post.metadata.get("author", "Unknown"),
            "variables": list(variables),
            "frontmatter": post.metadata,
        }
