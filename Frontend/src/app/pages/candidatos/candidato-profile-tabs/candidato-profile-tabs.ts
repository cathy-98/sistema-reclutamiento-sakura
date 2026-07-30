import { CommonModule } from '@angular/common';
import { Component, EventEmitter, Input, Output } from '@angular/core';

export interface CandidatoProfileTab {
  id: string;
  label: string;
  icon: string;
}

@Component({
  selector: 'app-candidato-profile-tabs',
  imports: [CommonModule],
  templateUrl: './candidato-profile-tabs.html',
  styleUrl: './candidato-profile-tabs.scss',
})
export class CandidatoProfileTabs {
  @Input() tabs: CandidatoProfileTab[] = [];
  @Input() activeTab = '';
  @Output() activeTabChange = new EventEmitter<string>();
}
