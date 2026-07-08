const API = "http://127.0.0.1:5000"

export function getStoredUser(){
    try{
        return JSON.parse(localStorage.getItem("user") || "{}")
    }catch{
        clearStoredUser()
        return {}
    }
}

export function saveStoredUser(user:any){
    localStorage.setItem("user", JSON.stringify(user))
}

export function clearStoredUser(){
    localStorage.removeItem("user")
}

export function authHeaders(){
    const user = getStoredUser()
    return user.token ? { Authorization: `Bearer ${user.token}` } : {}
}

export async function api(path:string, options:any = {}){
    const hasBody = options.body !== undefined
    const res = await fetch(`${API}${path}`, {
        ...options,
        headers: {
            ...(hasBody ? { "Content-Type": "application/json" } : {}),
            ...authHeaders(),
            ...(options.headers || {})
        }
    })

    const result = await res.json().catch(() => ({}))

    if(!res.ok || result.success === false){
        if(res.status===401){
            clearStoredUser()
        }
        throw new Error(result.error || result.message || "Request failed")
    }

    return Object.prototype.hasOwnProperty.call(result, "data") ? result.data : result
}

export function escapeHtml(value:any){
    return String(value ?? "")
        .replaceAll("&", "&amp;")
        .replaceAll("<", "&lt;")
        .replaceAll(">", "&gt;")
        .replaceAll('"', "&quot;")
}
