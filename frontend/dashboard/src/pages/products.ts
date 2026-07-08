import { renderCrudPage } from "./crud"

export async function renderProducts(){
    await renderCrudPage({
        module:"Products",
        title:"Products",
        endpoint:"products",
        fields:[
            {key:"name",label:"Name",required:true},
            {key:"price",label:"Price",type:"number",required:true},
            {key:"stock",label:"Stock",type:"number",required:true}
        ]
    })
}
