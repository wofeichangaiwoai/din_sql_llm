
* The final place to call the llm with prompt
langchain.llms.base.BaseLLM.generate_prompt
```markdown
        print("<<<<<======>>>>>"*10)
        from langchain.utils.input import get_colored_text
        print(get_colored_text(prompt_strings, "green"))
        print(">>>>>>>"*10)
```


langchain.llms.base.LLM._generate

```
    def _generate(
        self,
        prompts: List[str],
        stop: Optional[List[str]] = None,
        run_manager: Optional[CallbackManagerForLLMRun] = None,
        **kwargs: Any,
    ) -> LLMResult:
        """Run the LLM on the given prompt and input."""
        # TODO: add caching here.
        generations = []
        new_arg_supported = inspect.signature(self._call).parameters.get("run_manager")
        for prompt in prompts:
            text = (
                self._call(prompt, stop=stop, run_manager=run_manager, **kwargs)
                if new_arg_supported
                else self._call(prompt, stop=stop, **kwargs)
            )
            generations.append([Generation(text=text)])
        return LLMResult(generations=generations)
```
