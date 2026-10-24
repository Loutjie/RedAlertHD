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

using System.Collections.Immutable;
using System.Linq;
using System.Text.RegularExpressions;

namespace OpenRA.Mods.Mobius.FileSystem
{
	public class RemasterFileSystemLoader : ContentSourcesFileSystem
	{
		// Each {Key} in these paths is replaced with the value of that ContentSource setting.
		// The defaults are the Tiberian Dawn HD audio files; an empty list keeps the mod's own list.
		[Desc("Voices files to use when the remaster content source is selected.")]
		public readonly ImmutableArray<string> RemasterVoices = [
			"cnchd|audio/voices-base.yaml",
			"cnchd|audio/voices-{AudioLanguage}-{AudioStyle}.yaml",
		];

		[Desc("Notifications files to use when the remaster content source is selected.")]
		public readonly ImmutableArray<string> RemasterNotifications = [
			"cnchd|audio/notifications-base.yaml",
			"cnchd|audio/notifications-{AudioLanguage}-{AudioStyle}.yaml",
		];

		[Desc("Music files to use when the remaster content source is selected.")]
		public readonly ImmutableArray<string> RemasterMusic = ["cnchd|audio/music-{MusicStyle}.yaml"];

		protected override bool InstallContentIfRequired(ModData modData)
		{
			if (base.InstallContentIfRequired(modData))
				return true;

			// Hack the mod manifest to set the requested variant
			void BodgeManifestPaths(Manifest manifest, string field, ImmutableArray<string> paths)
			{
				if (paths.IsEmpty)
					return;

				var expanded = paths.Select(p => Regex.Replace(p, @"\{(\w+)\}", m => sourceSettings[m.Groups[1].Value])).ToImmutableArray();
				manifest.GetType().GetField(field)?.SetValue(manifest, expanded);
			}

			if (sourceSettings.ContentSource == "remaster")
			{
				BodgeManifestPaths(modData.Manifest, "Voices", RemasterVoices);
				BodgeManifestPaths(modData.Manifest, "Notifications", RemasterNotifications);
				BodgeManifestPaths(modData.Manifest, "Music", RemasterMusic);
			}

			if (sourceSettings["ArtworkStyle"] != "remastered")
			{
				var wvs = modData.GetOrCreate<WorldViewportSizes>();
				wvs.GetType().GetField("DefaultScale")?.SetValue(wvs, 1.0f);
			}

			return false;
		}
	}
}
