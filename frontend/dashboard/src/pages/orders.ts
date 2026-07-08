import { renderCrudPage } from "./crud"
import { api } from "../api"

export async function renderOrders(){
    const options=await api("/order-options")
    const customers=options.customers || []
    const products=options.products || []
    const statuses=options.statuses || ["Pending","Processing","Completed","Cancelled"]

    await renderCrudPage({
        module:"Orders",
        title:"Orders",
        endpoint:"orders",
        fields:[
            {
                key:"customer_id",
                label:"Customer",
                required:true,
                displayKey:"customer_name",
                options:customers.map((customer:any)=>({value:customer.id,label:customer.name}))
            },
            {
                key:"product_id",
                label:"Product",
                required:true,
                displayKey:"product_name",
                options:products.map((product:any)=>({value:product.id,label:product.name}))
            },
            {key:"quantity",label:"Quantity",type:"number",required:true},
            {
                key:"status",
                label:"Status",
                required:true,
                options:statuses.map((status:string)=>({value:status,label:status}))
            }
        ]
    })
}
