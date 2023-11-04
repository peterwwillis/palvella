import flet as ft
import flet_fastapi

async def main(page: ft.Page):
    counter = ft.Text("0", size=50, data=0)

    async def add_click(e):
        counter.data += 1
        counter.value = str(counter.data)
        await counter.update_async()

    page.floating_action_button = ft.FloatingActionButton(
        icon=ft.icons.ADD, on_click=add_click
    )
    await page.add_async(
        ft.Container(counter, alignment=ft.alignment.center, expand=True)
    )

    async def add_clicked(e):
        await page.add_async(
            ft.Checkbox(label=new_task.value)
        )
        new_task.value = ""
        await new_task.focus_async()
        await new_task.update_async()

    new_task = ft.TextField(hint_text="Whats needs to be done?", width=300)
    await page.add_async(
        ft.Row(
            [
                new_task,
                ft.ElevatedButton("Add", on_click=add_clicked)
            ]
        )
    )


app = flet_fastapi.app(main)
