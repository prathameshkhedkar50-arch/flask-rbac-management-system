import { getModulePermission } from "../permissions"
import { api, escapeHtml } from "../api"
import { confirmDialog, emptyState, pageLoading, setBusy, showToast } from "../ui"

export async function renderUsers(){
    const el=document.getElementById("content")
    if(!el)return
    const content:HTMLElement=el

    content.innerHTML=pageLoading("Users","Loading users and roles...")

    const permission=await getModulePermission("Users")

    if(!permission.can_read){
        content.innerHTML=`
            <div class="page">
                <div class="access-denied">
                    <h2>Access Denied</h2>
                    <p>You do not have permission to view users.</p>
                </div>
            </div>
        `
        return
    }

    let users:any[]=[]
    let roles:any[]=[]
    let editing:any=null
    let message=""
    let messageColor="green"
    let loading=false
    let saving=false
    let deletingId:number | null=null

    async function load(){
        users=await api("/users")
        roles=await api("/role-options")
    }

    function roleOptions(selected:any){
        return roles.map(role=>`
            <option value="${role.id}" ${Number(selected)===role.id ? "selected" : ""}>
                ${escapeHtml(role.name)}
            </option>
        `).join("")
    }

    function render(){
        const canShowForm=(permission.can_create && !editing) || (permission.can_update && editing)

        content.innerHTML=`
            <div class="page">
                <div class="page-header">
                    <div>
                        <p class="eyebrow">Administration</p>
                        <h1 class="page-title">Users</h1>
                        <p class="page-subtitle">Create users, assign roles, and maintain access ownership.</p>
                    </div>
                    <span class="badge">${users.length} users</span>
                </div>

                ${canShowForm ? `
                    <form id="userForm" class="form-panel">
                        <label class="field">
                            <span class="field-label">Username</span>
                            <input id="username" value="${escapeHtml(editing?.username || "")}" class="input">
                        </label>
                        <label class="field">
                            <span class="field-label">Password</span>
                            <input id="password" type="password" placeholder="${editing ? "Leave blank to keep" : ""}" class="input">
                        </label>
                        <label class="field">
                            <span class="field-label">Role</span>
                            <select id="role_id" class="select">
                                ${roleOptions(editing?.role_id)}
                            </select>
                        </label>
                        <button type="submit" class="btn btn-primary">
                            ${editing ? "Update" : "Add"} User
                        </button>
                        ${editing ? `<button type="button" id="cancelEdit" class="btn btn-secondary">Cancel</button>` : ""}
                    </form>
                ` : ""}

                <p class="message ${messageColor==="red" ? "error" : "success"}">${escapeHtml(message)}</p>

                ${loading ? `<div class="panel"><div class="loading"><span class="spinner"></span> Refreshing users...</div></div>` : ""}
                <div class="table-wrap ${loading ? "is-muted" : ""}">
                    <table class="data-table">
                        <tr>
                            <th>Username</th>
                            <th>Role</th>
                            ${(permission.can_update || permission.can_delete) ? `<th>Actions</th>` : ""}
                        </tr>
                        ${users.map(user=>`
                            <tr>
                                <td>${escapeHtml(user.username)}</td>
                                <td><span class="badge">${escapeHtml(user.role_name)}</span></td>
                                ${(permission.can_update || permission.can_delete) ? `
                                    <td>
                                        <div class="table-actions">
                                            ${permission.can_update ? `<button class="editUser btn btn-secondary" data-id="${user.id}" ${saving || deletingId!==null ? "disabled" : ""}>Edit</button>` : ""}
                                            ${permission.can_delete ? `<button class="deleteUser btn btn-danger" data-id="${user.id}" ${saving || deletingId!==null ? "disabled" : ""}>
                                                ${deletingId===user.id ? `<span class="spinner tiny"></span>Deleting` : "Delete"}
                                            </button>` : ""}
                                        </div>
                                    </td>
                                ` : ""}
                            </tr>
                        `).join("") || `
                            <tr>
                                <td colspan="${2 + ((permission.can_update || permission.can_delete) ? 1 : 0)}">
                                    ${emptyState("No users found","Users will appear here after they are created.")}
                                </td>
                            </tr>
                        `}
                    </table>
                </div>
            </div>
        `

        const form=document.getElementById("userForm") as HTMLFormElement | null

        if(form){
            form.onsubmit=async(event)=>{
                event.preventDefault()
                if(saving)return

                const payload={
                    username:(document.getElementById("username") as HTMLInputElement).value,
                    password:(document.getElementById("password") as HTMLInputElement).value,
                    role_id:Number((document.getElementById("role_id") as HTMLSelectElement).value)
                }

                try{
                    saving=true
                    setBusy(form.querySelector("button[type='submit']") as HTMLButtonElement | null,true,editing ? "Updating..." : "Saving...")
                    if(editing){
                        await api(`/users/${editing.id}`,{
                            method:"PUT",
                            body:JSON.stringify(payload)
                        })
                    }else{
                        await api("/users",{
                            method:"POST",
                            body:JSON.stringify(payload)
                        })
                    }

                    editing=null
                    saving=false
                    message="Saved successfully"
                    messageColor="green"
                    showToast("User saved successfully","success")
                    loading=true
                    render()
                    await load()
                    loading=false
                    render()
                }catch(err:any){
                    saving=false
                    loading=false
                    message=err.message || "Unable to save user"
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

        document.querySelectorAll(".editUser").forEach(btn=>{
            btn.addEventListener("click",()=>{
                const id=Number((btn as HTMLElement).dataset.id)
                editing=users.find(user=>user.id===id)
                message=""
                render()
            })
        })

        document.querySelectorAll(".deleteUser").forEach(btn=>{
            btn.addEventListener("click",async()=>{
                const id=Number((btn as HTMLElement).dataset.id)

                const confirmed=await confirmDialog(
                    "Delete User",
                    "This will permanently delete this user account.",
                    "Delete"
                )

                if(!confirmed){
                    return
                }

                try{
                    deletingId=id
                    render()
                    await api(`/users/${id}`,{
                        method:"DELETE"
                    })
                    message="Deleted successfully"
                    messageColor="green"
                    showToast("User deleted successfully","success")
                    loading=true
                    render()
                    await load()
                    deletingId=null
                    loading=false
                    render()
                }catch(err:any){
                    deletingId=null
                    loading=false
                    message=err.message || "Unable to delete user"
                    messageColor="red"
                    showToast(message,"error")
                    render()
                }
            })
        })
    }

    try{
        await load()
        render()
    }catch(err:any){
        content.innerHTML=`
            <div class="page">
                <div class="page-header">
                    <div>
                        <p class="eyebrow">Administration</p>
                        <h1 class="page-title">Users</h1>
                    </div>
                </div>
                <div class="access-denied">
                    <p>${escapeHtml(err.message || "Unable to load users")}</p>
                </div>
            </div>
        `
    }
}
