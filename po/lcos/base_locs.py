class BaseLocs:
    ByText = lambda text: f'"{text}"'
    ByButtonText = lambda name: f'button:has-text(\"{name}\")'
    Loading = 'span.ant-spin-dot, ant-spin-nested-loading'
