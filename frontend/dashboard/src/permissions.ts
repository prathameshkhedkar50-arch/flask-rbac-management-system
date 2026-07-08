import { api, getStoredUser, saveStoredUser } from "./api"

type PermissionRow={
    module:string
    can_create:boolean
    can_read:boolean
    can_update:boolean
    can_delete:boolean
}

async function loadPermissions():Promise<PermissionRow[]>{
    const user=getStoredUser()

    if(!user.token){
        return []
    }

    if(Array.isArray(user.permissions)){
        return user.permissions
    }

    const permissions=await api("/my-permissions")
    user.permissions=permissions
    saveStoredUser(user)

    return permissions
}

export function clearPermissionCache(){
    const user=getStoredUser()
    delete user.permissions
    delete user.menus
    saveStoredUser(user)
}

export async function getModulePermission(module:string){
    const permissions=await loadPermissions()
    const target=module.toLowerCase()

    return permissions.find(p=>p.module===target) || {
        module:target,
        can_create:false,
        can_read:false,
        can_update:false,
        can_delete:false
    }
}

export async function canCreate(module:string){
    return (await getModulePermission(module)).can_create
}

export async function canRead(module:string){
    return (await getModulePermission(module)).can_read
}

export async function canUpdate(module:string){
    return (await getModulePermission(module)).can_update
}

export async function canDelete(module:string){
    return (await getModulePermission(module)).can_delete
}
