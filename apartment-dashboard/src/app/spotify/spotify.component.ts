import { Component, OnInit } from '@angular/core';
import {ApiService} from "../api.service";
import {FormControl} from "@angular/forms";
import {SpotifyResponse} from "../spotifyResponse";

@Component({
  selector: 'app-spotify',
  templateUrl: './spotify.component.html',
  styleUrls: ['./spotify.component.css']
})
export class SpotifyComponent implements OnInit {

  searchBar = new FormControl('');
  showSearch: boolean = false;
  playlistSelection = new FormControl('');
  currentlyPlaying: SpotifyResponse;
  notPlayingMsg = "Nothing's happening right now.";
  play = true;
  playlists: SpotifyResponse[];
  searchResults: SpotifyResponse[];
  displaySearchModal: boolean = false;
  showSearchModalResults: boolean = false;

  constructor(private api:ApiService) { }

  ngOnInit(): void {
    // Get the currently playing song.
    this.getCurrentlyPlaying();

    // Get all of the current user's playlists.
    this.api.spotifyGetPlaylists()
      .subscribe( resp => {
        this.playlists = resp;
      });
  }

  /**
   * Search for a song using the API endpoint.
   */
  search() {
    // Get search query.
    let query = this.searchBar.value;
    if (query != ''){
      // Perform the search.
      this.api.spotifySearch(query)
        .subscribe( resp =>{
          if (this.displaySearchModal) {
            this.showSearchModalResults = true;
          }
          else {
            this.showSearch = true;
          }
          // Display results.
          this.searchResults = resp;
        }
      );
    }
  }

  /**
   * Pause/resume the playback.
   */
  updatePlaybackState() {
    // Flip the play state.
    this.play = !this.play
    // Update the API.
    this.api.spotifyUpdatePlaybackState(this.play)
      .subscribe( resp => {
          console.log(resp);
      });
  }

  /**
   * Begin the playlist.
   */
  startPlaylist() {
    // Get playlist URI.
    let uri = this.playlistSelection.value;
    // Start the playlist.
    this.api.spotifyStartPlayback(uri, true)
      .subscribe( resp => {
        console.log(resp);
      });
  }

  /**
   * Add a song from one of the search results.
   */
  addToQueue(uri){
    // Check if there is a song playing. If not, play the selected song.
    if (this.currentlyPlaying === undefined || this.currentlyPlaying.error){
      this.api.spotifyStartPlayback(uri, false)
        .subscribe(resp => {
          console.log(resp);
        })
    }
    // Add a song to the queue if there is a song playing.
    else {
      this.api.spotifyAdd(uri)
      .subscribe( resp => {
        console.log(resp);
      });
    }
    this.showSearch = false;
  }

  /**
   * Get the metadata for the currently playing track.
   */
  getCurrentlyPlaying(){
    this.api.spotifyGetCurrentlyPlaying()
      .subscribe( resp => {
          this.currentlyPlaying = resp;
          // Display the song that is currently playing if there is one.
          if (this.currentlyPlaying !== undefined && !this.currentlyPlaying.error){
            this.notPlayingMsg = '';
          }
        });
  }

}

