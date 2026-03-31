<!--
This is an exploration of how to add community membership to a record.  We had a published record
before.  We submitted a request to assign it to a community.  A request ID was generated. We then 
took the request ID and approved it, so the record became published.  Maybe if we had added the 
community while the record was still in draft, it wouldn't have been so hard... 
-->



curl -k --request POST \
     --url 'https://127.0.0.1:5000/api/communities/cecf1612-5f83-4bb0-98c1-4c4fb963ef78/records' \
     --header 'Authorization: Bearer PIErNEHI2tLp8yLl8R8QofSCEPgn0kCp7bPxXKXqFjMed2SvdQO7tniLtWoB' \
     --header 'Content-Type: application/json' \
     --data '{"record_id": "s5mvp-eg647"}'


export RECORD_ID="s5mvp-eg647"
export COMMUNITY_ID="cecf1612-5f83-4bb0-98c1-4c4fb963ef78"  # community UUID
export BASE="https://127.0.0.1:5000"
export TOKEN="PIErNEHI2tLp8yLl8R8QofSCEPgn0kCp7bPxXKXqFjMed2SvdQO7tniLtWoB"

curl -k -X POST "$BASE/api/records/$RECORD_ID/communities" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{
    "communities": [
      {"id": "'$COMMUNITY_ID'"}
    ]
  }'


<!-- this above request assumes curator level over the community, but it didn't work all in one step, 
we still had to approve the request.  Maybe it would be better to attempt a non-privileged request and then
approve it, as the below curl does 
--> 

curl -i -X PUT "$BASE/api/records/$RECORD_ID/draft/review" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{
    "receiver": {
      "community": "'$COMMUNITY_ID'"
    },
    "type": "community-submission"
  }'

<!--
Regardless, the request returned a request ID, which has to be accepted by the curator/administrator.  
The response from the server was:
-->

{
  "processed": [
    {
      "community_id": "cecf1612-5f83-4bb0-98c1-4c4fb963ef78",
      "request": {
        "created": "2026-03-30T23:06:08.607708+00:00",
        "created_by": {
          "user": "3"
        },
        "expires_at": null,
        "id": "bb2b1be0-a81d-4dd2-b348-f9d33e881f47",
        "is_closed": false,
        "is_expired": false,
        "is_open": true,
        "links": {
          "actions": {
            "accept": "https://0.0.0.0:5000/api/requests/bb2b1be0-a81d-4dd2-b348-f9d33e881f47/actions/accept",
            "cancel": "https://0.0.0.0:5000/api/requests/bb2b1be0-a81d-4dd2-b348-f9d33e881f47/actions/cancel",
            "decline": "https://0.0.0.0:5000/api/requests/bb2b1be0-a81d-4dd2-b348-f9d33e881f47/actions/decline"
          },
          "comments": "https://0.0.0.0:5000/api/requests/bb2b1be0-a81d-4dd2-b348-f9d33e881f47/comments",
          "self": "https://0.0.0.0:5000/api/requests/bb2b1be0-a81d-4dd2-b348-f9d33e881f47",
          "self_html": "https://0.0.0.0:5000/requests/bb2b1be0-a81d-4dd2-b348-f9d33e881f47",
          "timeline": "https://0.0.0.0:5000/api/requests/bb2b1be0-a81d-4dd2-b348-f9d33e881f47/timeline"
        },
        "number": "3",
        "receiver": {
          "community": "cecf1612-5f83-4bb0-98c1-4c4fb963ef78"
        },
        "revision_id": 3,
        "status": "submitted",
        "title": "Organoids to model liver disease",
        "topic": {
          "record": "s5mvp-eg647"
        },
        "type": "community-inclusion",
        "updated": "2026-03-30T23:06:08.668878+00:00"
      },
      "request_id": "bb2b1be0-a81d-4dd2-b348-f9d33e881f47"
    }
  ]
}


<!-- 
Which is a request record. Notice the "request_id" field. We need to collect the request ID and then accept the request by sending an accept message.  Let us look at where in the record the request id can be found:

["processed"][$INDEX]["request"][]"id"] = "bb2b1be0-a81d-4dd2-b348-f9d33e881f47"
["processed"][$INDEX]["request"]["receiver"]["community"] = "cecf1612-5f83-4bb0-98c1-4c4fb963ef78"
["processed'][$INDEX]["request"]{"topic"]["record"] = "s5mvp-eg647"

So all the information we need to approve for each record is inside the ["request"] JSON subobject

-->

<!-- now approve the request -->

curl -X 'POST' \
  'https://127.0.0.1:5000/api/requests/bb2b1be0-a81d-4dd2-b348-f9d33e881f47/actions/accept' \
  -H 'accept: application/json' \
  -H 'Authorization: Bearer PIErNEHI2tLp8yLl8R8QofSCEPgn0kCp7bPxXKXqFjMed2SvdQO7tniLtWoB' \
  -H 'Content-Type: application/json' \
  -d '{
  "payload": {
    "content": "Your request has been accepted!",
    "format": "html"
  }
}'

URL: https://127.0.0.1:5000/api/requests/bb2b1be0-a81d-4dd2-b348-f9d33e881f47/actions/accept

<!-- server response: -->

{
  "id": "bb2b1be0-a81d-4dd2-b348-f9d33e881f47",
  "created": "2026-03-30T23:06:08.607708+00:00",
  "updated": "2026-03-31T01:36:08.305407+00:00",
  "links": {
    "actions": {},
    "self": "https://0.0.0.0:5000/api/requests/bb2b1be0-a81d-4dd2-b348-f9d33e881f47",
    "self_html": "https://0.0.0.0:5000/requests/bb2b1be0-a81d-4dd2-b348-f9d33e881f47",
    "comments": "https://0.0.0.0:5000/api/requests/bb2b1be0-a81d-4dd2-b348-f9d33e881f47/comments",
    "timeline": "https://0.0.0.0:5000/api/requests/bb2b1be0-a81d-4dd2-b348-f9d33e881f47/timeline"
  },
  "revision_id": 4,
  "type": "community-inclusion",
  "title": "Organoids to model liver disease",
  "number": "3",
  "status": "accepted",
  "is_closed": true,
  "is_open": false,
  "expires_at": null,
  "is_expired": false,
  "created_by": {
    "user": "3"
  },
  "receiver": {
    "community": "cecf1612-5f83-4bb0-98c1-4c4fb963ef78"
  },
  "topic": {
    "record": "s5mvp-eg647"
  }
}

<!-->
Now, the community membership is there. Lets see if the record is still listed as draft or not.  It is
listed as published and not draft! 
-->

curl -X 'GET' \
  'https://127.0.0.1:5000/api/records/s5mvp-eg647' \
  -H 'accept: application/json' \
  -H 'Authorization: Bearer PIErNEHI2tLp8yLl8R8QofSCEPgn0kCp7bPxXKXqFjMed2SvdQO7tniLtWoB'


{
  "id": "s5mvp-eg647",
  "created": "2026-03-16T22:13:19.570952+00:00",
  "updated": "2026-03-16T22:13:19.635908+00:00",
  "links": {
    "self": "https://0.0.0.0:5000/api/records/s5mvp-eg647",
    "self_html": "https://0.0.0.0:5000/records/s5mvp-eg647",
    "preview_html": "https://0.0.0.0:5000/records/s5mvp-eg647?preview=1",
    "reserve_doi": "https://0.0.0.0:5000/api/records/s5mvp-eg647/draft/pids/doi",
    "parent": "https://0.0.0.0:5000/api/records/33m2b-j1b55",
    "parent_html": "https://0.0.0.0:5000/records/33m2b-j1b55",
    "self_iiif_manifest": "https://0.0.0.0:5000/api/iiif/record:s5mvp-eg647/manifest",
    "self_iiif_sequence": "https://0.0.0.0:5000/api/iiif/record:s5mvp-eg647/sequence/default",
    "files": "https://0.0.0.0:5000/api/records/s5mvp-eg647/files",
    "media_files": "https://0.0.0.0:5000/api/records/s5mvp-eg647/media-files",
    "thumbnails": {
      "10": "https://0.0.0.0:5000/api/iiif/record:s5mvp-eg647:liver_initial_19_Review-Organoids%20to%20model%20liver%20disease.pdf/full/%5E10,/0/default.jpg",
      "50": "https://0.0.0.0:5000/api/iiif/record:s5mvp-eg647:liver_initial_19_Review-Organoids%20to%20model%20liver%20disease.pdf/full/%5E50,/0/default.jpg",
      "100": "https://0.0.0.0:5000/api/iiif/record:s5mvp-eg647:liver_initial_19_Review-Organoids%20to%20model%20liver%20disease.pdf/full/%5E100,/0/default.jpg",
      "250": "https://0.0.0.0:5000/api/iiif/record:s5mvp-eg647:liver_initial_19_Review-Organoids%20to%20model%20liver%20disease.pdf/full/%5E250,/0/default.jpg",
      "750": "https://0.0.0.0:5000/api/iiif/record:s5mvp-eg647:liver_initial_19_Review-Organoids%20to%20model%20liver%20disease.pdf/full/%5E750,/0/default.jpg",
      "1200": "https://0.0.0.0:5000/api/iiif/record:s5mvp-eg647:liver_initial_19_Review-Organoids%20to%20model%20liver%20disease.pdf/full/%5E1200,/0/default.jpg"
    },
    "archive": "https://0.0.0.0:5000/api/records/s5mvp-eg647/files-archive",
    "archive_media": "https://0.0.0.0:5000/api/records/s5mvp-eg647/media-files-archive",
    "latest": "https://0.0.0.0:5000/api/records/s5mvp-eg647/versions/latest",
    "latest_html": "https://0.0.0.0:5000/records/s5mvp-eg647/latest",
    "versions": "https://0.0.0.0:5000/api/records/s5mvp-eg647/versions",
    "draft": "https://0.0.0.0:5000/api/records/s5mvp-eg647/draft",
    "access_links": "https://0.0.0.0:5000/api/records/s5mvp-eg647/access/links",
    "access_grants": "https://0.0.0.0:5000/api/records/s5mvp-eg647/access/grants",
    "access_users": "https://0.0.0.0:5000/api/records/s5mvp-eg647/access/users",
    "access_groups": "https://0.0.0.0:5000/api/records/s5mvp-eg647/access/groups",
    "access_request": "https://0.0.0.0:5000/api/records/s5mvp-eg647/access/request",
    "access": "https://0.0.0.0:5000/api/records/s5mvp-eg647/access",
    "communities": "https://0.0.0.0:5000/api/records/s5mvp-eg647/communities",
    "communities-suggestions": "https://0.0.0.0:5000/api/records/s5mvp-eg647/communities-suggestions",
    "requests": "https://0.0.0.0:5000/api/records/s5mvp-eg647/requests"
  },
  "revision_id": 4,
  "parent": {
    "id": "33m2b-j1b55",
    "access": {
      "grants": [],
      "owned_by": {
        "user": "3"
      },
      "links": [],
      "settings": {
        "allow_user_requests": false,
        "allow_guest_requests": false,
        "accept_conditions_text": null,
        "secret_link_expiration": 0
      }
    },
    "communities": {
      "ids": [
        "cecf1612-5f83-4bb0-98c1-4c4fb963ef78"
      ],
      "default": "cecf1612-5f83-4bb0-98c1-4c4fb963ef78",
      "entries": [
        {
          "id": "cecf1612-5f83-4bb0-98c1-4c4fb963ef78",
          "created": "2026-03-20T15:23:53.617297+00:00",
          "updated": "2026-03-27T20:09:18.148155+00:00",
          "links": {},
          "revision_id": 10,
          "slug": "som",
          "metadata": {
            "title": "SOM",
            "description": "The Standard Organoid Modeling project",
            "curation_policy": "<p>All submissions will be reviewed by a curator before publishing.&nbsp;</p>",
            "page": "<p>The Standardized Organoid Modeling (SOM) Center will serve as a first-of-its-kind NIH-wide integrated platform dedicated to developing standardized organoid-based New Approach Methodologies (NAMs). The initiative is being launched by the NIH Division of Program Coordination, Planning, and Strategic Initiatives, in collaboration with many other NIH Institutes, Centers, and Offices, including the National Cancer Institute (NCI), the National Institute of Allergy and Infectious Diseases&rsquo; (NIAID) Research Technologies Branch and Center for Human Immunology, Infection and Autoimmunity, the National Human Genome Research Institute (NHGRI) the National Center for Advancing Translational Sciences (NCATS), and the Office of Research on Women&rsquo;s Health, with plans to expand partnerships across many other NIH institutes and centers and the broader scientific community.</p>",
            "type": {
              "id": "project"
            },
            "website": "http://nih.gov/som",
            "organizations": [
              {
                "name": "NIAID"
              }
            ]
          },
          "access": {
            "visibility": "public",
            "members_visibility": "public",
            "member_policy": "open",
            "record_submission_policy": "open",
            "review_policy": "closed"
          },
          "custom_fields": {},
          "is_verified": false,
          "deletion_status": {
            "is_deleted": false,
            "status": "P"
          },
          "children": {
            "allow": false
          }
        }
      ]
    },
    "pids": {},
    "is_verified": false
  },
  "versions": {
    "is_latest": true,
    "is_latest_draft": true,
    "index": 1
  },
  "is_published": true,
  "is_draft": false,
  "pids": {
    "oai": {
      "identifier": "oai:idss-archive.com:s5mvp-eg647",
      "provider": "oai"
    }
  },
  "metadata": {
    "resource_type": {
      "id": "publication-article",
      "title": {
        "cs": "Článek v časopise",
        "de": "Zeitschriftenartikel",
        "en": "Journal article",
        "sv": "Tidskriftsartikel"
      }
    },
    "creators": [
      {
        "person_or_org": {
          "type": "personal",
          "name": "Nuciforo, Sandro",
          "given_name": "Sandro",
          "family_name": "Nuciforo"
        }
      },
      {
        "person_or_org": {
          "type": "personal",
          "name": "Heim, Markus",
          "given_name": "Markus",
          "family_name": "Heim"
        }
      }
    ],
    "title": "Organoids to model liver disease",
    "publisher": "",
    "publication_date": "2020-10-22",
    "description": "Liver disease is a critical public health concern, responsible for over two million deaths annually, largely stemming from chronic liver disease (CLD) associated with factors like viral infections, excessive alcohol consumption, and non-alcoholic fatty liver disease (NAFLD). Traditional models for studying liver diseases have limitations, primarily relying on cell lines or animal models that do not replicate human liver biology effectively, leading to challenges in therapeutic development. The advent of organoid technology presents a breakthrough, enabling the cultivation of three-dimensional (3D) structures that mimic the functional characteristics of human organs. This review focuses on the development and application of liver organoids in the context of liver disease modeling.\n\nThe core methodology for generating liver organoids involves isolating stem or progenitor cells that can self-organize into structures resembling liver tissue. These organoids can be derived from patient biopsies or pluripotent stem cells, allowing for the cultivation of personalized models that maintain genetic stability over time. The simplicity of the culture methods, which build on previous work with intestinal organoids, allows robust growth and long-term maintenance of liver organoids. Such organoids preserve the complexity of liver tissue, thereby providing a more physiologically relevant model that is suitable for exploring liver function, drug metabolism, and disease progression.\n\nThe review highlights significant advances in the application of liver organoids to study various liver diseases. For instance, organoids derived from patients with Alagille syndrome exhibited impaired biliary differentiation, reflecting the disease's hepatic manifestations. Similarly, organoids generated from individuals with alpha-1 antitrypsin deficiency successfully modeled key pathological features, including misfolding and accumulation of the A1AT protein. Furthermore, the organoid models demonstrated potential for studying metabolic diseases, such as Wilson's disease, and were used to investigate drug efficacy in the context of steatohepatitis.\n\nLiver organoids also hold promise in translational research, facilitating drug testing and personalized medicine approaches. The ability to derive organoids from patient tissues provides insights into individual responses to therapies, which can guide treatment decisions. These models can also be combined with genetic editing techniques, such as CRISPR/Cas9, to explore the functional implications of specific mutations in the context of liver health and disease.\n\nDespite the exciting potential of liver organoids, limitations persist. Current models often lack full maturation into hepatocyte-like cells, and co-cultures with other liver cell types (like endothelial and immune cells) remain challenging but are critical for mimicking the complexity of liver pathology. The success rates for organoid establishment from adult tissues can be low, posing a challenge for access to patient samples. Moreover, existing protocols primarily focus on epithelial cells, neglecting the other critical cellular components of liver tissue that contribute to its overall functionality.\n\nFuture research should aim to enhance the maturation and functional capabilities of liver organoids, explore co-culture systems incorporating multiple cell types, and improve the efficiency of organoid generation. Developing better culture conditions and novel extracellular matrix systems could significantly advance the utility of liver organoids for modeling complex liver diseases and for therapeutic applications in regenerative medicine.\n\nThis review underscores the transformative impact of organoid technology in liver disease research, providing a framework for future investigations that leverage these innovative models to address pressing challenges in the understanding and treatment of liver diseases."
  },
  "custom_fields": {},
  "access": {
    "record": "public",
    "files": "public",
    "embargo": {
      "active": false,
      "reason": null
    },
    "status": "open"
  },
  "files": {
    "enabled": true,
    "order": [],
    "count": 1,
    "total_bytes": 1586501,
    "entries": {
      "liver_initial_19_Review-Organoids to model liver disease.pdf": {
        "id": "7ebaecea-46b4-474f-8ff1-e534f99dc167",
        "checksum": "md5:68bdd0832cfb4dae064e1303f9a8e3ec",
        "ext": "pdf",
        "size": 1586501,
        "mimetype": "application/pdf",
        "storage_class": "L",
        "key": "liver_initial_19_Review-Organoids to model liver disease.pdf",
        "metadata": null,
        "access": {
          "hidden": false
        },
        "links": {
          "self": "https://0.0.0.0:5000/api/records/s5mvp-eg647/files/liver_initial_19_Review-Organoids%20to%20model%20liver%20disease.pdf",
          "content": "https://0.0.0.0:5000/api/records/s5mvp-eg647/files/liver_initial_19_Review-Organoids%20to%20model%20liver%20disease.pdf/content",
          "iiif_canvas": "https://0.0.0.0:5000/api/iiif/record:s5mvp-eg647/canvas/liver_initial_19_Review-Organoids%20to%20model%20liver%20disease.pdf",
          "iiif_base": "https://0.0.0.0:5000/api/iiif/record:s5mvp-eg647:liver_initial_19_Review-Organoids%20to%20model%20liver%20disease.pdf",
          "iiif_info": "https://0.0.0.0:5000/api/iiif/record:s5mvp-eg647:liver_initial_19_Review-Organoids%20to%20model%20liver%20disease.pdf/info.json",
          "iiif_api": "https://0.0.0.0:5000/api/iiif/record:s5mvp-eg647:liver_initial_19_Review-Organoids%20to%20model%20liver%20disease.pdf/full/full/0/default.png"
        }
      }
    }
  },
  "media_files": {
    "enabled": false,
    "order": [],
    "count": 0,
    "total_bytes": 0,
    "entries": {}
  },
  "status": "published",
  "deletion_status": {
    "is_deleted": false,
    "status": "P"
  },
  "internal_notes": [],
  "stats": {
    "this_version": {
      "views": 2,
      "unique_views": 2,
      "downloads": 2,
      "unique_downloads": 2,
      "data_volume": 3173002
    },
    "all_versions": {
      "views": 2,
      "unique_views": 2,
      "downloads": 2,
      "unique_downloads": 2,
      "data_volume": 3173002
    }
  }
}

<!-- 
the complete record is displayed and showed it is published.  the webpage showed the record
belonged to the corrrect community, as well
-->

