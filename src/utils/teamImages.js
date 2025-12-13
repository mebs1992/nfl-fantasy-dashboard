/**
 * Team Image Utilities
 * Maps team names to image URLs or generates placeholder images
 */

// Team image mappings - these can be updated with actual URLs from NFL.com
export const getTeamImageUrl = (teamName, logoUrl = null) => {
  // If we have a logo URL from the API, use it (and make it larger)
  if (logoUrl) {
    // Replace size parameters to get larger images (128x128 instead of 40x40)
    const largerLogo = logoUrl.replace(/[?&]x=\d+[&]?/, '').replace(/[?&]y=\d+[&]?/, '')
    // If no size params were found, add them
    if (largerLogo === logoUrl) {
      const separator = logoUrl.includes('?') ? '&' : '?'
      return `${logoUrl}${separator}x=128&y=128`
    }
    // Add larger size params
    const separator = largerLogo.includes('?') ? '&' : '?'
    return `${largerLogo}${separator}x=128&y=128`
  }
  
  // Fallback: Use team name to generate a consistent color/avatar
  // For now, we'll use a placeholder service that generates avatars based on team name
  const encodedName = encodeURIComponent(teamName)
  return `https://ui-avatars.com/api/?name=${encodedName}&size=128&background=667eea&color=fff&bold=true&font-size=0.5`
}

// Team color schemes for visual consistency
export const getTeamColors = (teamName) => {
  const colors = {
    "Maggi's Mighty Ducks": { primary: '#FFD700', secondary: '#FFA500', gradient: 'linear-gradient(135deg, #FFD700 0%, #FFA500 100%)' },
    "Mebs Militia": { primary: '#8B0000', secondary: '#DC143C', gradient: 'linear-gradient(135deg, #8B0000 0%, #DC143C 100%)' },
    "Pels": { primary: '#00CED1', secondary: '#20B2AA', gradient: 'linear-gradient(135deg, #00CED1 0%, #20B2AA 100%)' },
    "Wolfpack": { primary: '#4B0082', secondary: '#8A2BE2', gradient: 'linear-gradient(135deg, #4B0082 0%, #8A2BE2 100%)' },
    "The Brotherhood": { primary: '#000000', secondary: '#333333', gradient: 'linear-gradient(135deg, #000000 0%, #333333 100%)' },
    "The Generous": { primary: '#32CD32', secondary: '#228B22', gradient: 'linear-gradient(135deg, #32CD32 0%, #228B22 100%)' },
    "The Ratpack": { primary: '#FF6347', secondary: '#FF4500', gradient: 'linear-gradient(135deg, #FF6347 0%, #FF4500 100%)' },
    "Woody": { primary: '#8B4513', secondary: '#A0522D', gradient: 'linear-gradient(135deg, #8B4513 0%, #A0522D 100%)' },
    "cheeseheads": { primary: '#FFD700', secondary: '#FFA500', gradient: 'linear-gradient(135deg, #FFD700 0%, #FFA500 100%)' },
    "DirtyBirds": { primary: '#000080', secondary: '#0000CD', gradient: 'linear-gradient(135deg, #000080 0%, #0000CD 100%)' },
    "Killer Cam": { primary: '#FF1493', secondary: '#DC143C', gradient: 'linear-gradient(135deg, #FF1493 0%, #DC143C 100%)' },
    "Scrubs": { primary: '#808080', secondary: '#A9A9A9', gradient: 'linear-gradient(135deg, #808080 0%, #A9A9A9 100%)' }
  }
  
  return colors[teamName] || { 
    primary: '#667eea', 
    secondary: '#764ba2', 
    gradient: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)' 
  }
}

// Fun team nicknames or tags
export const getTeamTagline = (teamName) => {
  const taglines = {
    "Maggi's Mighty Ducks": "Quack Attack!",
    "Mebs Militia": "Locked and Loaded",
    "Pels": "Soaring High",
    "Wolfpack": "Howling for Wins",
    "The Brotherhood": "United We Stand",
    "The Generous": "Giving Points Away",
    "The Ratpack": "Squeaking By",
    "Woody": "Rooted in Victory",
    "cheeseheads": "Cheesy Goodness",
    "DirtyBirds": "Flying Dirty",
    "Killer Cam": "Cam-tastic",
    "Scrubs": "Scrubbing the Competition"
  }
  
  return taglines[teamName] || "Ready to Play"
}

