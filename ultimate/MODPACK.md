# Ultimate modpack inventory

This inventory records the mod list supplied for the target Eaglercraft Ultimate 1.6.4 pack. It is a planning reference, not a statement that each item has already been tested on a dedicated server.

## Content and gameplay mods

- Aether II
- Alfheim
- Applied Energistics
- Archimedes' Ships
- AutoPackager
- Better Dungeons
- Big Reactors
- Biomes O' Plenty
- BuildCraft
- ChickenChunks
- Compact Solar Arrays
- Damage Indicators
- DartCraft
- Eagler Celebrities
- Eaglercraft
- EnderStorage
- Ex Nihilo
- Extra Utilities
- Fast Leaf Decay
- Forge Microblocks
- Galacticraft Mars
- Hats
- Iguana Tweaks for Tinkers Construct
- IndustrialCraft 2
- Inventory Tweaks
- Iron Chest
- JABBA
- Legendary Beats
- Lucky Block
- Lycanites Desert Mobs
- Lycanites Mobs
- Lycanites Plains Mobs
- Magical Crops
- MineFactory Reloaded
- Morph
- Natura
- Not Enough Items
- Nuclear Control
- OpenBlocks
- OpenMods
- Railcraft
- Redstone Arsenal
- Roguelike Dungeons
- Thaumcraft
- The Secret Rooms Mod
- The Twilight Forest
- Thermal Expansion
- TiC Tooltips
- Tinkers' Construct
- Tinkers' Merchworks
- TooMuchTNT
- Tree Growing Simulator 2014
- Waila
- Waila Harvestability
- Witchery
- YUNoMakeGoodMap

## Platform and library components

- Forge Mod Loader
- Minecraft Coder Pack
- Minecraft Forge
- Minecraft Multipart Plugin
- iChunUtil

## Compatibility work groups

| Work group | Examples | Validation required |
|---|---|---|
| World generation | Biomes O' Plenty, Natura, Roguelike Dungeons | Matching server worldgen and dimension registration |
| Dimensions | Aether II, Alfheim, Galacticraft Mars, Twilight Forest | Dimension IDs, portals, travel, respawn and chunk persistence |
| Machines and automation | Applied Energistics, BuildCraft, Big Reactors, IC2, Thermal Expansion, MineFactory Reloaded, Railcraft | Tile entity state, inventories, energy/fluid networks, ticking and custom payloads |
| Mobs and entities | Lycanites Mobs and variants, Morph, Hats | Entity registration, spawn logic, metadata, AI and tracking |
| Items and inventories | Tinkers' Construct, Iguana Tweaks, Iron Chest, EnderStorage, Lucky Block | Item IDs, NBT, containers, recipes and server-authoritative actions |
| Building and blocks | Forge Microblocks, Secret Rooms, OpenBlocks | Block/item registries, tile entities, multipart placement and rendering state |
| Client-only/interface | Damage Indicators, Inventory Tweaks, NEI, Waila, TiC Tooltips, YUNoMakeGoodMap | Identify client-only components; do not require them on the dedicated server unless their mod metadata says otherwise |

## Required next input

The browser bundle does not include the individual original mod JARs or a dedicated server distribution. Before claiming complete modpack support, the project needs a matching server-side mod set and exact mod versions/configuration. The client-side mod roster alone is insufficient to recreate server behavior.
