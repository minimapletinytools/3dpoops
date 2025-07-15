# Hose Adaptors

## hoseadaptor_with_sidehole.scad / hoseadaptor_with_sidehole_tapered.scad

Hose adaptors with a side port. The simple version has you specify the inner and outer diameters explicitly. The tapered version has you specify the tip and base diameters and the wall thickness. You can make a straight fitting by setting the tip and base diameters to the same value.

### Common Dust Hose Diameters

```
// connects to 4" Dustrite quickchange handle
top_taper_diameter_tip = 63.5;     
top_taper_diameter_base = 63;     
top_is_outer_fitting = true;    
```

```
// connects to the locline 2.5" shop vaccum adaptor (Loc-Line - 81209)
bot_taper_diameter_tip = 106;     
bot_taper_diameter_base = 106; 
bot_is_outer_fitting = false;    
```