import { renderStaticPage } from "./staticPage"

export function renderReports(){
    renderStaticPage(
        "Reports",
        "Documents",
        "A structured reporting surface for role-controlled business summaries.",
        [
            {title:"Operational Reports",text:"Review activity summaries and module-level status in a consistent layout."},
            {title:"Export Ready",text:"This section is prepared for future report actions and filters."},
            {title:"Access Controlled",text:"Visibility continues to follow the existing sidebar and route permission flow."}
        ]
    )
}
