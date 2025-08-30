from rusty_tags import *

tabs = Div(
    Nav(
        Button('Account', type='button', role='tab', id='demo-tabs-with-panels-tab-1', aria_controls='demo-tabs-with-panels-panel-1', aria_selected='true', tabindex='0'),
        Button('Password', type='button', role='tab', id='demo-tabs-with-panels-tab-2', aria_controls='demo-tabs-with-panels-panel-2', aria_selected='false', tabindex='0'),
        role='tablist',
        aria_orientation='horizontal',
        cls='w-full'
    ),
    Div(
        Div(
            Header(
                H2('Account'),
                P("Make changes to your account here. Click save when you're done.")
            ),
            Section(
                Form(
                    Div(
                        Label('Name', fr='demo-tabs-account-name'),
                        Input(type='text', id='demo-tabs-account-name', value='Pedro Duarte'),
                        cls='grid gap-3'
                    ),
                    Div(
                        Label('Username', fr='demo-tabs-account-username'),
                        Input(type='text', id='demo-tabs-account-username', value='@peduarte'),
                        cls='grid gap-3'
                    ),
                    cls='form grid gap-6'
                )
            ),
            Footer(
                Button('Save changes', type='button', cls='btn')
            ),
            cls='card'
        ),
        role='tabpanel',
        id='demo-tabs-with-panels-panel-1',
        aria_labelledby='demo-tabs-with-panels-tab-1',
        tabindex='-1',
        aria_selected='true'
    ),
    Div(
        Div(
            Header(
                H2('Password'),
                P("Change your password here. After saving, you'll be logged out.")
            ),
            Section(
                Form(
                    Div(
                        Label('Current password', fr='demo-tabs-password-current'),
                        Input(type='password', id='demo-tabs-password-current'),
                        cls='grid gap-3'
                    ),
                    Div(
                        Label('New password', fr='demo-tabs-password-new'),
                        Input(type='password', id='demo-tabs-password-new'),
                        cls='grid gap-3'
                    ),
                    cls='form grid gap-6'
                )
            ),
            Footer(
                Button('Save Password', type='button', cls='btn')
            ),
            cls='card'
        ),
        role='tabpanel',
        id='demo-tabs-with-panels-panel-2',
        aria_labelledby='demo-tabs-with-panels-tab-2',
        tabindex='-1',
        aria_selected='false',
        hidden=''
    ),
    id='demo-tabs-with-panels',
    cls='tabs w-full'
)