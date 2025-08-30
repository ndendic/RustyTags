from rusty_tags import *

sidebar = Aside(
    Nav(
        Section(
            Div(
                H3('Getting started', id='group-label-content-1'),
                Ul(
                    Li(
                        A(
                            Svg(
                                Path(d='m7 11 2-2-2-2'),
                                Path(d='M11 13h4'),
                                Rect(width='18', height='18', x='3', y='3', rx='2', ry='2'),
                                xmlns='http://www.w3.org/2000/svg',
                                width='24',
                                height='24',
                                viewbox='0 0 24 24',
                                fill='none',
                                stroke='currentColor',
                                stroke_width='2',
                                stroke_linecap='round',
                                stroke_linejoin='round'
                            ),
                            Span('Playground'),
                            href='#'
                        )
                    ),
                    Li(
                        A(
                            Svg(
                                Path(d='M12 8V4H8'),
                                Rect(width='16', height='12', x='4', y='8', rx='2'),
                                Path(d='M2 14h2'),
                                Path(d='M20 14h2'),
                                Path(d='M15 13v2'),
                                Path(d='M9 13v2'),
                                xmlns='http://www.w3.org/2000/svg',
                                width='24',
                                height='24',
                                viewbox='0 0 24 24',
                                fill='none',
                                stroke='currentColor',
                                stroke_width='2',
                                stroke_linecap='round',
                                stroke_linejoin='round'
                            ),
                            Span('Models'),
                            href='#'
                        )
                    ),
                    Li(
                        Details(
                            Summary(
                                Svg(
                                    Path(d='M12.22 2h-.44a2 2 0 0 0-2 2v.18a2 2 0 0 1-1 1.73l-.43.25a2 2 0 0 1-2 0l-.15-.08a2 2 0 0 0-2.73.73l-.22.38a2 2 0 0 0 .73 2.73l.15.1a2 2 0 0 1 1 1.72v.51a2 2 0 0 1-1 1.74l-.15.09a2 2 0 0 0-.73 2.73l.22.38a2 2 0 0 0 2.73.73l.15-.08a2 2 0 0 1 2 0l.43.25a2 2 0 0 1 1 1.73V20a2 2 0 0 0 2 2h.44a2 2 0 0 0 2-2v-.18a2 2 0 0 1 1-1.73l.43-.25a2 2 0 0 1 2 0l.15.08a2 2 0 0 0 2.73-.73l.22-.39a2 2 0 0 0-.73-2.73l-.15-.08a2 2 0 0 1-1-1.74v-.5a2 2 0 0 1 1-1.74l.15-.09a2 2 0 0 0 .73-2.73l-.22-.38a2 2 0 0 0-2.73-.73l-.15.08a2 2 0 0 1-2 0l-.43-.25a2 2 0 0 1-1-1.73V4a2 2 0 0 0-2-2z'),
                                    Circle(cx='12', cy='12', r='3'),
                                    xmlns='http://www.w3.org/2000/svg',
                                    width='24',
                                    height='24',
                                    viewbox='0 0 24 24',
                                    fill='none',
                                    stroke='currentColor',
                                    stroke_width='2',
                                    stroke_linecap='round',
                                    stroke_linejoin='round'
                                ),
                                'Settings',
                                aria_controls='submenu-content-1-3-content'
                            ),
                            Ul(
                                Li(
                                    A(
                                        Span('General'),
                                        href='#'
                                    )
                                ),
                                Li(
                                    A(
                                        Span('Team'),
                                        href='#'
                                    )
                                ),
                                Li(
                                    A(
                                        Span('Billing'),
                                        href='#'
                                    )
                                ),
                                Li(
                                    A(
                                        Span('Limits'),
                                        href='#'
                                    )
                                ),
                                id='submenu-content-1-3-content'
                            ),
                            id='submenu-content-1-3'
                        )
                    )
                ),
                role='group',
                aria_labelledby='group-label-content-1'
            ),
            cls='scrollbar'
        ),
        aria_label='Sidebar navigation'
    ),
    data_side='left',
    aria_hidden='false',
    cls='sidebar'
)

navbar = Header(
    Div(
        Button(
            Svg(
                Rect(width='18', height='18', x='3', y='3', rx='2'),
                Path(d='M9 3v18'),
                xmlns='http://www.w3.org/2000/svg',
                width='24',
                height='24',
                viewbox='0 0 24 24',
                fill='none',
                stroke='currentColor',
                stroke_width='2',
                stroke_linecap='round',
                stroke_linejoin='round'
            ),
            type='button',
            onclick="document.dispatchEvent(new CustomEvent('basecoat:sidebar'))",
            aria_label='Toggle sidebar',
            data_tooltip='Toggle sidebar',
            data_side='bottom',
            data_align='start',
            cls='btn-sm-icon-ghost mr-auto size-7 -ml-1.5'
        ),
        Select(
            Option('Default', value=''),
            Option('Claude', value='claude'),
            Option('Doom 64', value='doom-64'),
            Option('Supabase', value='supabase'),
            id='theme-select',
            cls='select h-8 leading-none'
        ),
        Script("(() => {\r\n      const themeSelect = document.getElementById('theme-select');\r\n      const storedTheme = localStorage.getItem('themeVariant');\r\n      if (themeSelect && storedTheme) themeSelect.value = storedTheme;\r\n      themeSelect.addEventListener('change', () => {\r\n        const newTheme = themeSelect.value;\r\n        document.documentElement.classList.forEach(c => {\r\n          if (c.startsWith('theme-')) document.documentElement.classList.remove(c);\r\n        });\r\n        if (newTheme) {\r\n          document.documentElement.classList.add(`theme-${newTheme}`);\r\n          localStorage.setItem('themeVariant', newTheme);\r\n        } else {\r\n          localStorage.removeItem('themeVariant');\r\n        }\r\n      });\r\n    })();"),
        Button(
            Span(
                Svg(
                    Circle(cx='12', cy='12', r='4'),
                    Path(d='M12 2v2'),
                    Path(d='M12 20v2'),
                    Path(d='m4.93 4.93 1.41 1.41'),
                    Path(d='m17.66 17.66 1.41 1.41'),
                    Path(d='M2 12h2'),
                    Path(d='M20 12h2'),
                    Path(d='m6.34 17.66-1.41 1.41'),
                    Path(d='m19.07 4.93-1.41 1.41'),
                    xmlns='http://www.w3.org/2000/svg',
                    width='24',
                    height='24',
                    viewbox='0 0 24 24',
                    fill='none',
                    stroke='currentColor',
                    stroke_width='2',
                    stroke_linecap='round',
                    stroke_linejoin='round'
                ),
                cls='hidden dark:block'
            ),
            Span(
                Svg(
                    Path(d='M12 3a6 6 0 0 0 9 9 9 9 0 1 1-9-9Z'),
                    xmlns='http://www.w3.org/2000/svg',
                    width='24',
                    height='24',
                    viewbox='0 0 24 24',
                    fill='none',
                    stroke='currentColor',
                    stroke_width='2',
                    stroke_linecap='round',
                    stroke_linejoin='round'
                ),
                cls='block dark:hidden'
            ),
            type='button',
            aria_label='Toggle dark mode',
            data_tooltip='Toggle dark mode',
            data_side='bottom',
            onclick="document.dispatchEvent(new CustomEvent('basecoat:theme'))",
            cls='btn-icon-outline size-8'
        ),
        A(
            Svg(
                Path(d='M15 22v-4a4.8 4.8 0 0 0-1-3.5c3 0 6-2 6-5.5.08-1.25-.27-2.48-1-3.5.28-1.15.28-2.35 0-3.5 0 0-1 0-3 1.5-2.64-.5-5.36-.5-8 0C6 2 5 2 5 2c-.3 1.15-.3 2.35 0 3.5A5.403 5.403 0 0 0 4 9c0 3.5 3 5.5 6 5.5-.39.49-.68 1.05-.85 1.65-.17.6-.22 1.23-.15 1.85v4'),
                Path(d='M9 18c-4.51 2-5-2-7-2'),
                xmlns='http://www.w3.org/2000/svg',
                width='24',
                height='24',
                viewbox='0 0 24 24',
                fill='none',
                stroke='currentColor',
                stroke_width='2',
                stroke_linecap='round',
                stroke_linejoin='round'
            ),
            href='https://github.com/hunvreus/basecoat',
            target='_blank',
            rel='noopener noreferrer',
            data_tooltip='GitHub repository',
            data_side='bottom',
            data_align='end',
            cls='btn-icon size-8'
        ),
        cls='flex h-14 w-full items-center gap-2 px-4'
    ),
    cls='bg-background sticky inset-x-0 top-0 isolate flex shrink-0 items-center gap-2 border-b z-10'
)

toggle_sidebar = Button('Toggle sidebar', type='button', onclick="document.dispatchEvent(new CustomEvent('basecoat:sidebar'))")