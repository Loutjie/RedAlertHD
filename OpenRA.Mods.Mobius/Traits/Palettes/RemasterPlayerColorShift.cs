#region Copyright & License Information
/*
 * Copyright (c) The OpenRA Developers and Contributors
 * This file is part of OpenRA, which is free software. It is made
 * available to you under the terms of the GNU General Public License
 * as published by the Free Software Foundation, either version 3 of
 * the License, or (at your option) any later version. For more
 * information, see COPYING.
 */
#endregion

using OpenRA.Mods.Common.Traits;
using OpenRA.Traits;

namespace OpenRA.Mods.Mobius.Traits
{
	[Desc("PlayerColorShift that is always constructed after the player palettes it shifts,",
		"even when map rules replace PlayerColorPalette with IndexedPlayerPalette after this trait is defined.")]
	public class RemasterPlayerColorShiftInfo : PlayerColorShiftInfo, NotBefore<PlayerColorPaletteInfo>, NotBefore<IndexedPlayerPaletteInfo>
	{
		public override object Create(ActorInitializer init) { return new PlayerColorShift(this); }
	}
}
