import { useEffect, useState } from "react";
const API = import.meta.env.VITE_API_URL || "http://localhost:8000";
export default function App() {
  const [email,setEmail]=useState(""); const [password,setPassword]=useState("");
  const [token,setToken]=useState(localStorage.getItem("token")||"");
  const [url,setUrl]=useState(""); const [items,setItems]=useState([]);
  const [message,setMessage]=useState(""); const [mode,setMode]=useState("login");
  async function request(path, options={}) {
    const response=await fetch(API+path,{...options,headers:{"Content-Type":"application/json",...(token?{Authorization:`Bearer ${token}`}:{}) ,...(options.headers||{})}});
    const data=await response.json().catch(()=>({}));
    if(!response.ok) throw new Error(data.detail||"Ocorreu um erro.");
    return data;
  }
  async function load(){try{setItems(await request("/urls"));}catch(e){setMessage(e.message);}}
  useEffect(()=>{if(token)load();},[token]);
  async function auth(e){e.preventDefault();try{
    if(mode==="register"){await request("/auth/register",{method:"POST",body:JSON.stringify({email,password})});setMessage("Cadastro realizado. Agora entre na sua conta.");setMode("login");}
    else {const d=await request("/auth/login",{method:"POST",body:JSON.stringify({email,password})});localStorage.setItem("token",d.access_token);setToken(d.access_token);setMessage("Login realizado.");}
  }catch(err){setMessage(err.message);}}
  async function create(e){e.preventDefault();try{const d=await request("/urls",{method:"POST",body:JSON.stringify({original_url:url})});setUrl("");setMessage(`Link criado: ${d.short_url}`);load();}catch(err){setMessage(err.message);}}
  function logout(){localStorage.removeItem("token");setToken("");setItems([]);}
  return <main className="shell"><header><div className="mark">↗</div><div><h1>Link<span>Curto</span></h1><p>Seus links, simples e organizados.</p></div></header>
    {!token?<section className="panel"><h2>{mode==="login"?"Acesse sua conta":"Crie sua conta"}</h2><form onSubmit={auth}><label>E-mail</label><input type="email" required value={email} onChange={e=>setEmail(e.target.value)} placeholder="voce@email.com"/><label>Senha</label><input type="password" minLength="8" required value={password} onChange={e=>setPassword(e.target.value)} placeholder="Mínimo de 8 caracteres"/><button>{mode==="login"?"Entrar":"Cadastrar"}</button></form><p className="switch" onClick={()=>setMode(mode==="login"?"register":"login")}>{mode==="login"?"Não tem conta? Cadastre-se":"Já tem conta? Entrar"}</p></section>
    :<><section className="panel"><div className="paneltop"><h2>Encurtar URL</h2><button className="ghost" onClick={logout}>Sair</button></div><form onSubmit={create}><label>URL original</label><input type="url" required value={url} onChange={e=>setUrl(e.target.value)} placeholder="https://exemplo.com/pagina"/><button>Gerar link curto</button></form></section><section className="panel"><h2>Meus links</h2>{items.length===0?<p className="muted">Você ainda não criou links.</p>:items.map(x=><article className="link" key={x.id}><div><a href={x.short_url} target="_blank" rel="noreferrer">{x.short_url}</a><p>{x.original_url}</p></div><button className="copy" onClick={()=>navigator.clipboard.writeText(x.short_url)}>Copiar</button></article>)}</section></>}
    {message&&<p className="message">{message}</p>}<footer>FastAPI · React · Redis</footer></main>
}
