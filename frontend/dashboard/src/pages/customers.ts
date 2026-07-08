import { renderCrudPage } from "./crud"

export async function renderCustomers(){
    await renderCrudPage({
        module:"Customers",
        title:"Customers",
        endpoint:"customers",
        fields:[
            {key:"name",label:"Name",required:true},
            {key:"phone",label:"Phone"},
            {key:"email",label:"Email",type:"email"}
        ]
    })
}
