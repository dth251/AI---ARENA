import { useEffect, useState } from 'react';
import { ImageOff } from 'lucide-react';
import type { MixConfig, Outfit } from '../../types';
export default function Avatar2D({ outfit, config }: { outfit: Outfit; config: MixConfig }) {
  const selectedAsset=outfit.assets.find(asset=>asset.colorCode===config.colorCode)||outfit.assets.find(asset=>!asset.colorCode);
  const layers=[{id:'base',url:outfit.baseAvatarUrl,zIndex:0},...(selectedAsset?[{...selectedAsset,zIndex:selectedAsset.zIndex??10}]:[]),...outfit.accessories.filter(a=>config.accessoryCodes.includes(a.code)).map(a=>({id:a.code,url:a.assetUrl,zIndex:a.zIndex??20})),...(outfit.otherLayers||[])].sort((a,b)=>(a.zIndex??30)-(b.zIndex??30));
  const signature=layers.map(layer=>layer.url).join('|');const [failed,setFailed]=useState(false);
  useEffect(()=>setFailed(false),[signature]);
  return <div className="avatar-stage"><div className="stage-arch"/><div className="stage-floor"/>{!selectedAsset||!outfit.baseAvatarUrl||failed?<div className="asset-missing"><ImageOff size={30}/><p>Chưa thể hiển thị lớp trang phục.</p><small>Hãy thử màu khác hoặc kiểm tra tài nguyên từ máy chủ.</small></div>:<div className="avatar-layers" role="img" aria-label={`Bản phối 2D ${outfit.name}`}>{layers.map(layer=><img key={layer.id} src={layer.url} alt="" onError={()=>setFailed(true)} style={{zIndex:layer.zIndex??30}}/>)}</div>}<span className="stage-label">2D MIX STUDIO <i/> LIVE PREVIEW</span></div>;
}
