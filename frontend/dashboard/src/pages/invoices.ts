import { renderStaticPage } from "./staticPage"

export function renderInvoices(){
    renderStaticPage(
        "Invoices",
        "Billing",
        "A polished invoice workspace ready for future billing records and approval flows.",
        [
            {title:"Invoice Queue",text:"Track billing documents and payment status from this module."},
            {title:"Review Workflow",text:"The page structure supports future approval and reconciliation actions."},
            {title:"Role Protected",text:"Access remains controlled by the existing RBAC sidebar and router checks."}
        ]
    )
}
