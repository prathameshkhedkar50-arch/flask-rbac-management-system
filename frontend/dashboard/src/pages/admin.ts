import { clearPermissionCache } from "../permissions"
import { api, escapeHtml, getStoredUser } from "../api"
import { confirmDialog, pageLoading, setBusy, showToast } from "../ui"

export async function renderAdmin(){

    const contentEl=document.getElementById("content")

    if(!contentEl)return

    const content:HTMLElement=contentEl

    const user=getStoredUser()
    const token=user.token

    if(!token){
        location.href="/login"
        return
    }

    content.innerHTML=pageLoading("Admin Management","Loading roles and permissions...")

    async function loadRoles(){
        return await api("/roles")
    }

    async function loadPermissions(roleId:number){
        return await api(`/permissions?role_id=${roleId}`)
    }

    async function savePermissions(data:any){
        return await api("/permissions/update",{
            method:"POST",
            body:JSON.stringify(data)
        })
    }

    let roles:any[]=await loadRoles()
    let selectedRole=roles[0]?.id
    let editingRole:any=null
    let roleMsg=""
    let roleMsgColor="green"
    let permissionMsg=""
    let permissionMsgColor="green"
    let savingRole=false
    let deletingRoleId:number | null=null
    let savingPermissions=false

    async function reloadRoles(){
        roles=await loadRoles()

        if(!roles.some(role=>role.id===selectedRole)){
            selectedRole=roles[0]?.id
        }
    }

    async function render(){
        const permissions=selectedRole ? await loadPermissions(selectedRole) : []

        content.innerHTML=`
        <div class="page section-grid">
            <div class="page-header">
                <div>
                    <p class="eyebrow">Administration</p>
                    <h1 class="page-title">Admin Management</h1>
                    <p class="page-subtitle">Manage roles, permissions, and CRUD access without changing the routing flow.</p>
                </div>
            </div>

            <section class="panel">
                <div class="panel-body">
                    <div class="toolbar">
                        <div>
                            <h2 class="section-title">Role Management</h2>
                            <p class="page-subtitle">Create custom roles and safely maintain role names.</p>
                        </div>
                        <span class="badge">${roles.length} roles</span>
                    </div>

                    <form id="roleForm" class="form-panel">
                        <label class="field">
                            <span class="field-label">Role Name</span>
                            <input id="roleName" value="${escapeHtml(editingRole?.name || "")}" class="input" required>
                        </label>
                        <button type="submit" class="btn btn-primary" ${savingRole ? "disabled" : ""}>
                            ${editingRole ? "Update Role" : "Create Role"}
                        </button>
                        ${editingRole ? `<button type="button" id="cancelRoleEdit" class="btn btn-secondary">Cancel</button>` : ""}
                    </form>

                    <p class="message ${roleMsgColor==="red" ? "error" : "success"}">${escapeHtml(roleMsg)}</p>

                    <div class="table-wrap">
                        <table class="data-table">
                            <tr>
                                <th>Role</th>
                                <th>Actions</th>
                            </tr>
                            ${roles.map(role=>`
                                <tr>
                                    <td><span class="badge">${escapeHtml(role.name)}</span></td>
                                    <td>
                                        ${role.name==="Admin" ? `
                                            <span class="badge">Protected</span>
                                        ` : `
                                            <div class="table-actions">
                                                <button class="editRole btn btn-secondary" data-id="${role.id}" ${savingRole || deletingRoleId!==null ? "disabled" : ""}>Edit</button>
                                                <button class="deleteRole btn btn-danger" data-id="${role.id}" ${savingRole || deletingRoleId!==null ? "disabled" : ""}>
                                                    ${deletingRoleId===role.id ? `<span class="spinner tiny"></span>Deleting` : "Delete"}
                                                </button>
                                            </div>
                                        `}
                                    </td>
                                </tr>
                            `).join("")}
                        </table>
                    </div>
                </div>
            </section>

            <section class="panel">
                <div class="panel-body">
                    <div class="toolbar">
                        <div>
                            <h2 class="section-title">Permission Management</h2>
                            <p class="page-subtitle">Update Create, Read, Update, and Delete permissions per module.</p>
                        </div>
                        <label class="field compact">
                            <span class="field-label">Selected Role</span>
                            <select id="roleSelect" class="select">
                            ${roles.map(role=>`
                                <option value="${role.id}" ${role.id===selectedRole?"selected":""}>
                                    ${escapeHtml(role.name)}
                                </option>
                            `).join("")}
                            </select>
                        </label>
                    </div>

                    <div class="table-wrap">
                        <table class="data-table">
                            <tr>
                                <th>Module</th>
                                <th class="permission-cell">Create</th>
                                <th class="permission-cell">Read</th>
                                <th class="permission-cell">Update</th>
                                <th class="permission-cell">Delete</th>
                            </tr>

                            ${permissions.map((p:any)=>`
                                <tr>
                                    <td><strong>${escapeHtml(p.menu)}</strong></td>

                                    <td class="permission-cell">
                                        <input type="checkbox" class="perm perm-check" data-menu-id="${p.menu_id}" data-key="can_create" ${p.can_create?"checked":""} ${savingPermissions ? "disabled" : ""}>
                                    </td>

                                    <td class="permission-cell">
                                        <input type="checkbox" class="perm perm-check" data-menu-id="${p.menu_id}" data-key="can_read" ${p.can_read?"checked":""} ${savingPermissions ? "disabled" : ""}>
                                    </td>

                                    <td class="permission-cell">
                                        <input type="checkbox" class="perm perm-check" data-menu-id="${p.menu_id}" data-key="can_update" ${p.can_update?"checked":""} ${savingPermissions ? "disabled" : ""}>
                                    </td>

                                    <td class="permission-cell">
                                        <input type="checkbox" class="perm perm-check" data-menu-id="${p.menu_id}" data-key="can_delete" ${p.can_delete?"checked":""} ${savingPermissions ? "disabled" : ""}>
                                    </td>
                                </tr>
                            `).join("")}
                        </table>
                    </div>

                    <div class="toolbar toolbar-bottom">
                        <button id="saveBtn" class="btn btn-primary" ${savingPermissions ? "disabled" : ""}>
                            ${savingPermissions ? `<span class="spinner tiny"></span>Saving` : "Save Permissions"}
                        </button>
                        <p id="adminMsg" class="message ${permissionMsgColor==="red" ? "error" : "success"}">${escapeHtml(permissionMsg)}</p>
                    </div>
                </div>
            </section>
        </div>
        `

        document.getElementById("roleForm")!
        .addEventListener("submit",async(event)=>{
            event.preventDefault()
            if(savingRole)return

            const name=(document.getElementById("roleName") as HTMLInputElement).value

            try{
                savingRole=true
                setBusy(document.querySelector("#roleForm button[type='submit']") as HTMLButtonElement | null,true,editingRole ? "Updating..." : "Creating...")
                if(editingRole){
                    await api(`/roles/${editingRole.id}`,{
                        method:"PUT",
                        body:JSON.stringify({name})
                    })
                    roleMsg="Role updated successfully"
                }else{
                    const created=await api("/roles",{
                        method:"POST",
                        body:JSON.stringify({name})
                    })
                    selectedRole=created.id
                    roleMsg="Role created successfully"
                }

                roleMsgColor="green"
                editingRole=null
                savingRole=false
                showToast(roleMsg,"success")
                await reloadRoles()
                await render()
            }catch(err:any){
                savingRole=false
                roleMsg=err.message || "Unable to save role"
                roleMsgColor="red"
                showToast(roleMsg,"error")
                await render()
            }
        })

        document.getElementById("cancelRoleEdit")?.addEventListener("click",async()=>{
            editingRole=null
            roleMsg=""
            await render()
        })

        document.querySelectorAll(".editRole").forEach(btn=>{
            btn.addEventListener("click",async()=>{
                const id=Number((btn as HTMLElement).dataset.id)
                editingRole=roles.find(role=>role.id===id)
                roleMsg=""
                await render()
            })
        })

        document.querySelectorAll(".deleteRole").forEach(btn=>{
            btn.addEventListener("click",async()=>{
                const id=Number((btn as HTMLElement).dataset.id)
                const role=roles.find(role=>role.id===id)

                const confirmed=await confirmDialog(
                    "Delete Role",
                    `Delete ${role?.name || "this role"}? Roles assigned to users will be blocked by the backend.`,
                    "Delete"
                )

                if(!confirmed){
                    return
                }

                try{
                    deletingRoleId=id
                    await render()
                    await api(`/roles/${id}`,{
                        method:"DELETE"
                    })
                    roleMsg="Role deleted successfully"
                    roleMsgColor="green"
                    editingRole=null
                    deletingRoleId=null
                    showToast(roleMsg,"success")
                    await reloadRoles()
                    await render()
                }catch(err:any){
                    deletingRoleId=null
                    roleMsg=err.message || "Unable to delete role"
                    roleMsgColor="red"
                    showToast(roleMsg,"error")
                    await render()
                }
            })
        })

        document.getElementById("roleSelect")!
        .addEventListener("change",async(e:any)=>{
            selectedRole=Number(e.target.value)
            permissionMsg=""
            await render()
        })

        document.getElementById("saveBtn")!
        .addEventListener("click",async()=>{
            if(savingPermissions)return

            const updates:any[]=[]

            document.querySelectorAll(".perm")
            .forEach((el:any)=>{

                const menu_id=Number(el.dataset.menuId)
                const key=el.dataset.key
                const checked=el.checked

                if(!menu_id || !key)return

                let row=updates.find(x=>x.menu_id===menu_id)

                if(!row){
                    row={
                        menu_id,
                        can_create:false,
                        can_read:false,
                        can_update:false,
                        can_delete:false
                    }
                    updates.push(row)
                }

                row[key]=checked
            })

            if(!selectedRole || updates.length===0){
                permissionMsgColor="red"
                permissionMsg="No permission data to save"
                showToast(permissionMsg,"error")
                await render()
                return
            }

            try{
                savingPermissions=true
                await render()
                const result=await savePermissions({
                    role_id:selectedRole,
                    permissions:updates
                })

                clearPermissionCache()
                savingPermissions=false
                permissionMsgColor="green"
                permissionMsg=result?.message || "Permissions saved successfully"
                showToast(permissionMsg,"success")
                await render()
            }catch(err:any){
                savingPermissions=false
                permissionMsgColor="red"
                permissionMsg=err.message || "Unable to save permissions"
                showToast(permissionMsg,"error")
                await render()
            }
        })
    }

    await render()
}
