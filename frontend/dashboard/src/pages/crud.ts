import { getModulePermission } from "../permissions"
import { api, escapeHtml } from "../api"
import { confirmDialog, emptyState, pageLoading, setBusy, showToast } from "../ui"

type Field={
    key:string
    label:string
    type?:string
    required?:boolean
    displayKey?:string
    options?:{value:any,label:string}[]
}

type CrudOptions={
    module:string
    title:string
    endpoint:string
    fields:Field[]
}

export async function renderCrudPage(options:CrudOptions){
    const el=document.getElementById("content")
    if(!el)return
    const content:HTMLElement=el
    const itemName=options.title.endsWith("s") ? options.title.slice(0,-1) : options.title

    content.innerHTML=pageLoading(options.title,`Loading ${options.title.toLowerCase()}...`)

    const permission=await getModulePermission(options.module)

    if(!permission.can_read){
        content.innerHTML=`
            <div class="page">
                <div class="access-denied">
                    <h2>Access Denied</h2>
                    <p>You do not have permission to view ${options.title}.</p>
                </div>
            </div>
        `
        return
    }

    let rows:any[]=[]
    let editing:any=null
    let message=""
    let messageColor="green"
    let loading=false
    let saving=false
    let deletingId:number | null=null

    async function loadRows(){
        rows=await api(`/${options.endpoint}`)
    }

    function formHtml(){
        if(!permission.can_create && !editing){
            return ""
        }

        if(editing && !permission.can_update){
            return ""
        }

        return `
            <form id="crudForm" class="form-panel">
                ${options.fields.map(field=>`
                    <label class="field">
                        <span class="field-label">${field.label}</span>
                        ${field.options ? `
                            <select id="field_${field.key}" class="select" ${field.required ? "required" : ""}>
                                <option value="">Select ${field.label}</option>
                                ${field.options.map(option=>`
                                    <option value="${escapeHtml(option.value)}" ${String(editing ? editing[field.key] : "")===String(option.value) ? "selected" : ""}>
                                        ${escapeHtml(option.label)}
                                    </option>
                                `).join("")}
                            </select>
                        ` : `
                            <input
                                id="field_${field.key}"
                                type="${field.type || "text"}"
                                value="${escapeHtml(editing ? editing[field.key] : "")}"
                                class="input"
                                ${field.required ? "required" : ""}
                            >
                        `}
                    </label>
                `).join("")}
                <button type="submit" class="btn btn-primary">
                    ${editing ? "Update" : "Add"} ${itemName}
                </button>
                ${editing ? `<button type="button" id="cancelEdit" class="btn btn-secondary">Cancel</button>` : ""}
            </form>
        `
    }

    function render(){
        content.innerHTML=`
            <div class="page">
                <div class="page-header">
                    <div>
                        <p class="eyebrow">Management</p>
                        <h1 class="page-title">${options.title}</h1>
                        <p class="page-subtitle">Create, review, and maintain ${options.title.toLowerCase()} based on your role permissions.</p>
                    </div>
                    <span class="badge">${rows.length} records</span>
                </div>
                ${formHtml()}
                <p id="crudMsg" class="message ${messageColor==="red" ? "error" : "success"}">${escapeHtml(message)}</p>
                ${loading ? `<div class="panel"><div class="loading"><span class="spinner"></span> Refreshing records...</div></div>` : ""}
                <div class="table-wrap ${loading ? "is-muted" : ""}">
                    <table class="data-table">
                        <tr>
                            ${options.fields.map(field=>`<th>${field.label}</th>`).join("")}
                            ${(permission.can_update || permission.can_delete) ? `<th>Actions</th>` : ""}
                        </tr>
                        ${rows.map(row=>`
                            <tr>
                                ${options.fields.map(field=>`<td>${escapeHtml(row[field.displayKey || field.key])}</td>`).join("")}
                                ${(permission.can_update || permission.can_delete) ? `
                                    <td>
                                        <div class="table-actions">
                                            ${permission.can_update ? `<button class="editRow btn btn-secondary" data-id="${row.id}" ${saving || deletingId!==null ? "disabled" : ""}>Edit</button>` : ""}
                                            ${permission.can_delete ? `<button class="deleteRow btn btn-danger" data-id="${row.id}" ${saving || deletingId!==null ? "disabled" : ""}>
                                                ${deletingId===row.id ? `<span class="spinner tiny"></span>Deleting` : "Delete"}
                                            </button>` : ""}
                                        </div>
                                    </td>
                                ` : ""}
                            </tr>
                        `).join("") || `
                            <tr>
                                <td colspan="${options.fields.length + ((permission.can_update || permission.can_delete) ? 1 : 0)}">
                                    ${emptyState(`No ${options.title.toLowerCase()} found`,"Records will appear here when they are added.")}
                                </td>
                            </tr>
                        `}
                    </table>
                </div>
            </div>
        `

        const form=document.getElementById("crudForm") as HTMLFormElement | null

        if(form){
            form.onsubmit=async(event)=>{
                event.preventDefault()
                if(saving)return

                const payload:any={}

                options.fields.forEach(field=>{
                    const input=document.getElementById(`field_${field.key}`) as HTMLInputElement
                    payload[field.key]=field.type==="number" ? Number(input.value) : input.value
                })

                try{
                    saving=true
                    setBusy(form.querySelector("button[type='submit']") as HTMLButtonElement | null,true,editing ? "Updating..." : "Saving...")
                    if(editing){
                        await api(`/${options.endpoint}/${editing.id}`,{
                            method:"PUT",
                            body:JSON.stringify(payload)
                        })
                    }else{
                        await api(`/${options.endpoint}`,{
                            method:"POST",
                            body:JSON.stringify(payload)
                        })
                    }

                    editing=null
                    saving=false
                    message="Saved successfully"
                    messageColor="green"
                    showToast(`${itemName} saved successfully`,"success")
                    loading=true
                    render()
                    await loadRows()
                    loading=false
                    render()
                }catch(err:any){
                    saving=false
                    loading=false
                    message=err.message || "Unable to save"
                    messageColor="red"
                    showToast(message,"error")
                    render()
                }
            }
        }

        document.getElementById("cancelEdit")?.addEventListener("click",()=>{
            editing=null
            message=""
            render()
        })

        document.querySelectorAll(".editRow").forEach(btn=>{
            btn.addEventListener("click",()=>{
                const id=Number((btn as HTMLElement).dataset.id)
                editing=rows.find(row=>row.id===id)
                message=""
                render()
            })
        })

        document.querySelectorAll(".deleteRow").forEach(btn=>{
            btn.addEventListener("click",async()=>{
                const id=Number((btn as HTMLElement).dataset.id)

                const confirmed=await confirmDialog(
                    `Delete ${itemName}`,
                    `This will permanently delete this ${itemName.toLowerCase()}.`,
                    "Delete"
                )

                if(!confirmed){
                    return
                }

                try{
                    deletingId=id
                    render()
                    await api(`/${options.endpoint}/${id}`,{
                        method:"DELETE"
                    })
                    message="Deleted successfully"
                    messageColor="green"
                    showToast(`${itemName} deleted successfully`,"success")
                    loading=true
                    render()
                    await loadRows()
                    deletingId=null
                    loading=false
                    render()
                }catch(err:any){
                    deletingId=null
                    loading=false
                    message=err.message || "Unable to delete"
                    messageColor="red"
                    showToast(message,"error")
                    render()
                }
            })
        })
    }

    try{
        await loadRows()
        render()
    }catch(err:any){
        content.innerHTML=`
            <div class="page">
                <div class="page-header">
                    <div>
                        <p class="eyebrow">Management</p>
                        <h1 class="page-title">${options.title}</h1>
                    </div>
                </div>
                <div class="access-denied">
                    <p>${escapeHtml(err.message || "Unable to load data")}</p>
                </div>
            </div>
        `
    }
}
