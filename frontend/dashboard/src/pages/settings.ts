import { renderStaticPage } from "./staticPage"

export function renderSettings(){
    renderStaticPage(
        "Settings",
        "Configuration",
        "Organize application preferences and operational controls in one place.",
        [
            {title:"System Preferences",text:"Central space for future application configuration options."},
            {title:"Security Context",text:"Settings remain protected by the current route permission rules."},
            {title:"Administration Ready",text:"The layout is prepared for forms, switches, and policy controls."}
        ]
    )
}
