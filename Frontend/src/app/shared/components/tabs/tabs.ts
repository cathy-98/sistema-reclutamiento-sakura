import { CommonModule } from '@angular/common';
import { Component, EventEmitter, Input, Output } from '@angular/core';

export interface TabItem {
  id: string;
  label: string;
}

@Component({
  selector: 'app-tabs',
  imports: [CommonModule],
  templateUrl: './tabs.html',
  styleUrl: './tabs.scss',
})
export class Tabs {
  @Input() tabs: TabItem[] = [];
  @Input() activeTab = '';
  @Input() ariaLabel = 'Pestanas';
  @Output() activeTabChange = new EventEmitter<string>();
}
