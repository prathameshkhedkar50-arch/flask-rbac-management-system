import { renderCrudPage } from "./crud"

export async function renderSuppliers(){
    await renderCrudPage({
        module:"Suppliers",
        title:"Suppliers",
        endpoint:"suppliers",
        fields:[
            {key:"name",label:"Name",required:true},
            {key:"contact",label:"Contact"},
            {key:"company",label:"Company"}
        ]
    })
}
