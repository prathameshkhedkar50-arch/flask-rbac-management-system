import { renderStaticPage } from "./staticPage"

export function renderAnalytics(){
    renderStaticPage(
        "Analytics",
        "Insights",
        "Track operational signals and performance summaries from one clean workspace.",
        [
            {title:"Performance Snapshot",text:"Key indicators are prepared for fast executive review."},
            {title:"Trend Monitoring",text:"Use this area for revenue, order, and inventory movement insights."},
            {title:"Decision Support",text:"Analytics content can expand here without changing the RBAC routing flow."}
        ]
    )
}
