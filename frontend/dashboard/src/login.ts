import { api, saveStoredUser } from "./api"
import { setBusy, showToast } from "./ui"

export function renderLogin(){
    document.body.innerHTML=`
    <div class="login-screen">
        <div class="login-card">
            <div class="sidebar-brand login-brand">
                <div class="brand-mark">RB</div>
                <div>
                    <div class="brand-title">RBAC Admin</div>
                    <div class="brand-subtitle">Secure operations console</div>
                </div>
            </div>
            <h2>Welcome back</h2>
            <p>Sign in to continue to your permitted modules.</p>
            <div class="login-form">
                <label class="field">
                    <span class="field-label">Username</span>
                    <input id="u" class="input" placeholder="username"/>
                </label>
                <label class="field">
                    <span class="field-label">Password</span>
                    <input id="p" class="input" type="password" placeholder="password"/>
                </label>
                <button id="btn" class="btn btn-primary">Login</button>
                <p id="err" class="message error"></p>
            </div>
        </div>
    </div>
    `
    document.getElementById("btn")!.onclick=async()=>{
        const button=document.getElementById("btn") as HTMLButtonElement
        const username=(document.getElementById("u") as HTMLInputElement).value
        const password=(document.getElementById("p") as HTMLInputElement).value

        try{
            setBusy(button,true,"Signing in...")
            const data=await api("/login",{
                method:"POST",
                body:JSON.stringify({username,password})
            })
            saveStoredUser(data)
            location.href="/"
        }catch(err:any){
            setBusy(button,false)
            const message=err.message || "Invalid credentials"
            document.getElementById("err")!.innerText=message
            showToast(message,"error")
        }
    }
}
